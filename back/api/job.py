"""
就业数据爬取与分析 API
====================================

提供职位数据爬取、薪资分析、技能分析接口。
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import os
import re
import json
import time
import random
from typing import List, Dict, Any, Optional, Tuple

import requests
from bs4 import BeautifulSoup
import csv
from flask import Response

# 简单日志到文件
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'logs')
LOG_DIR = os.path.abspath(LOG_DIR)
os.makedirs(LOG_DIR, exist_ok=True)
CRAWL_LOG = os.path.join(LOG_DIR, 'crawl.log')

def _log(msg: str):
    try:
        with open(CRAWL_LOG, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except Exception:
        pass

job_bp = Blueprint('job', __name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'raw')
DATA_DIR = os.path.abspath(DATA_DIR)
os.makedirs(DATA_DIR, exist_ok=True)


def _save_json(items: List[Dict[str, Any]], tag: str = 'jobs') -> str:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(DATA_DIR, f'{tag}_{ts}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return path


def _list_json_files() -> List[str]:
    files = []
    for name in os.listdir(DATA_DIR):
        if name.startswith('jobs_') and name.endswith('.json'):
            files.append(os.path.join(DATA_DIR, name))
    
    # 优先选择jobs_50000_文件，然后jobs_5000_文件，最后其他文件
    jobs_50000_files = [f for f in files if 'jobs_50000_' in f]
    jobs_5000_files = [f for f in files if 'jobs_5000_' in f and 'jobs_50000_' not in f]
    other_files = [f for f in files if 'jobs_5000_' not in f and 'jobs_50000_' not in f]
    
    # 先返回jobs_50000_文件（按时间倒序），然后jobs_5000_文件，最后其他文件
    return sorted(jobs_50000_files, reverse=True) + sorted(jobs_5000_files, reverse=True) + sorted(other_files, reverse=True)


def _load_latest_jobs(limit_files: int = 1) -> List[Dict[str, Any]]:
    jobs: List[Dict[str, Any]] = []
    for p in _list_json_files()[:limit_files]:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                jobs.extend(json.load(f))
        except Exception as e:
            _log(f"Failed to load {p}: {e}")
            continue
    return jobs


def _parse_salary_to_numeric(s: str) -> float:
    if not s:
        return 0.0
    s = s.replace(' ', '')
    # 兼容 k/月、千/月、年薪 等常见写法，做一个尽量通用的解析
    m = re.findall(r"(\d+\.?\d*)", s)
    if not m:
        return 0.0
    nums = list(map(float, m))
    base = sum(nums) / len(nums)
    # 单位猜测
    if 'k' in s.lower():
        base *= 1000
    if '千' in s:
        base *= 1000
    if '万' in s:
        base *= 10000
    # 月/年折算（粗略）
    if '年' in s:
        base = base / 12.0
    return float(round(base, 2))


UA_POOL = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36',
]

def _headers() -> Dict[str, str]:
    return {
        'User-Agent': random.choice(UA_POOL),
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.baidu.com/'
    }

def _maybe_sleep(min_s: float = 0.8, max_s: float = 2.0):
    time.sleep(random.uniform(min_s, max_s))

def _get(url: str, timeout: int = 12, retries: int = 2) -> Optional[requests.Response]:
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers=_headers(), timeout=timeout)
            if resp.status_code == 200 and resp.text:
                return resp
            _log(f"GET non-200 {resp.status_code} {url}")
        except Exception as e:
            last_err = e
            _log(f"GET error {url}: {e}")
        _maybe_sleep()
    _log(f"GET failed after retries {url}: {last_err}")
    return None


def _crawl_51job(city_code: str, pages: int) -> List[Dict[str, Any]]:
    # 51job 的页面结构可能调整，这里以基础选择器为主，容错为辅
    base = f'https://search.51job.com/list/{city_code},000000,0000,00,9,99,%E6%8A%A4%E5%B7%A5,2,'
    items: List[Dict[str, Any]] = []
    for i in range(1, pages + 1):
        url = f'{base}{i}.html'
        resp = _get(url)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, 'html.parser')
        # 多套选择器兜底
        selectors = [
            'div.j_joblist div.e',                # 旧结构
            'div#joblist div.joblist div.joblist-item',
            'table#resultList .el'
        ]
        rows = []
        for sel in selectors:
            rows = soup.select(sel)
            if rows:
                break
        if not rows:
            _log(f"51job no rows matched on {url}")
        for row in rows:
            title = row.select_one('a')
            comp = row.select_one('a.cname') or row.select_one('.t2 a')
            area = row.select_one('span.d.at') or row.select_one('.t3')
            sal = row.select_one('span.sal') or row.select_one('.t4')
            t = (title.get_text(strip=True) if title else '')
            c = (comp.get_text(strip=True) if comp else '')
            city = (area.get_text(strip=True) if area else '')
            salary = (sal.get_text(strip=True) if sal else '')
            if t:
                items.append({
                    'title': t,
                    'company': c,
                    'location': city,
                    'salary': salary,
                    'source': '51job',
                    'crawl_time': datetime.now().isoformat()
                })
        _maybe_sleep(1.0, 2.0)
    return items


def _crawl_zhaopin(city_kw: str, pages: int) -> List[Dict[str, Any]]:
    # 智联采用查询参数，这里使用基本关键词页，结构可能随时间变化
    base = f'https://sou.zhaopin.com/?jl={city_kw}&kw=%E6%8A%A4%E5%B7%A5&kt=3&p='
    items: List[Dict[str, Any]] = []
    for i in range(1, pages + 1):
        url = f'{base}{i}'
        resp = _get(url)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, 'html.parser')
        selectors = [
            '.joblist-box .joblist-box__item',
            '.joblist .joblist-item',
            '.positionlist .positionlist__item'
        ]
        rows = []
        for sel in selectors:
            rows = soup.select(sel)
            if rows:
                break
        if not rows:
            _log(f"zhaopin no rows matched on {url}")
        for row in rows:
            t_el = row.select_one('.joblist-box__title a') or row.select_one('.job-title a') or row.select_one('a')
            c_el = row.select_one('.joblist-box__cname a') or row.select_one('.company-name a')
            a_el = row.select_one('.joblist-box__city') or row.select_one('.job-area')
            s_el = row.select_one('.joblist-box__salary') or row.select_one('.job-salary')
            t = t_el.get_text(strip=True) if t_el else ''
            c = c_el.get_text(strip=True) if c_el else ''
            city = a_el.get_text(strip=True) if a_el else ''
            salary = s_el.get_text(strip=True) if s_el else ''
            if t:
                items.append({
                    'title': t,
                    'company': c,
                    'location': city,
                    'salary': salary,
                    'source': 'zhaopin',
                    'crawl_time': datetime.now().isoformat()
                })
        _maybe_sleep(1.0, 2.0)
    return items


@job_bp.route('/api/job/crawl/start', methods=['POST'])
def start_crawl():
    data = request.get_json(silent=True) or {}
    pages = int(data.get('pages', 2))
    city = str(data.get('city', '010000'))  # 默认北京
    city_kw = data.get('city_kw', '北京')

    _log(f"crawl start pages={pages} city={city} city_kw={city_kw}")
    items: List[Dict[str, Any]] = []
    # 先尝试 51job，再尝试 智联
    part1 = _crawl_51job(city, pages)
    part2 = _crawl_zhaopin(city_kw, pages)
    items.extend(part1)
    items.extend(part2)
    _log(f"crawl results 51job={len(part1)} zhaopin={len(part2)} total={len(items)}")

    if not items:
        # 回退到最近一次成功文件
        latest = _list_json_files()[:1]
        if latest:
            try:
                with open(latest[0], 'r', encoding='utf-8') as f:
                    fallback = json.load(f)
                return jsonify({'success': True, 'message': '抓取为空，已回退到最近一次成功数据', 'data': {'count': len(fallback), 'file': os.path.basename(latest[0]), 'used_fallback': True}})
            except Exception:
                pass
        return jsonify({'success': False, 'message': '未抓取到有效数据，可能被目标站点限制或页面结构变更'}), 200

    path = _save_json(items, 'jobs')
    return jsonify({'success': True, 'message': '爬取完成', 'data': {'count': len(items), 'file': os.path.basename(path), 'used_fallback': False}})


@job_bp.route('/api/job/analysis/salary', methods=['GET'])
def analysis_salary():
    jobs = _load_latest_jobs()
    if not jobs:
        return jsonify({'success': True, 'data': {'total_avg': 0, 'city_avg': {}}})
    city_sum: Dict[str, float] = {}
    city_cnt: Dict[str, int] = {}
    for j in jobs:
        city = (j.get('location') or '').strip() or '未知'
        val = _parse_salary_to_numeric(j.get('salary', ''))
        if val <= 0:
            continue
        city_sum[city] = city_sum.get(city, 0.0) + val
        city_cnt[city] = city_cnt.get(city, 0) + 1
    city_avg = {k: round(city_sum[k] / max(city_cnt[k], 1), 2) for k in city_sum}
    total_vals = [v for v in city_avg.values() if v > 0]
    total_avg = round(sum(total_vals) / max(len(total_vals), 1), 2)
    return jsonify({'success': True, 'data': {'total_avg': total_avg, 'city_avg': city_avg}})


@job_bp.route('/api/job/analysis/skills', methods=['GET'])
def analysis_skills():
    jobs = _load_latest_jobs()
    if not jobs:
        return jsonify({'success': True, 'data': {'skill_counts': {}}})
    # 简单的技能关键词统计（示例）
    keywords = ['护理', '康复', '照护', '陪护', '老年', '持证', '评估', '沟通']
    counts: Dict[str, int] = {k: 0 for k in keywords}
    for j in jobs:
        text = (j.get('title', '') + ' ' + j.get('company', '')).lower()
        for k in keywords:
            if k.lower() in text:
                counts[k] += 1
    return jsonify({'success': True, 'data': {'skill_counts': counts}})


@job_bp.route('/api/job/data/import', methods=['POST'])
def import_job_data():
    """导入本地JSON/CSV数据，标准化为 data/raw/jobs_import_*.json"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未选择文件'}), 400
        f = request.files['file']
        if not f.filename:
            return jsonify({'success': False, 'message': '文件名为空'}), 400

        filename = f.filename.lower()
        rows: List[Dict[str, Any]] = []

        if filename.endswith('.json'):
            data = json.load(f)
            if isinstance(data, dict):
                data = data.get('items') or data.get('data') or []
            if not isinstance(data, list):
                return jsonify({'success': False, 'message': 'JSON结构不正确，应为数组或含 items/data 的对象'}), 400
            for it in data:
                rows.append({
                    'title': (it.get('title') or '').strip(),
                    'company': (it.get('company') or '').strip(),
                    'location': (it.get('location') or '').strip(),
                    'salary': (it.get('salary') or '').strip(),
                    'source': it.get('source') or 'import',
                    'crawl_time': it.get('crawl_time') or datetime.now().isoformat()
                })
        elif filename.endswith('.csv'):
            content = f.read().decode('utf-8', errors='ignore').splitlines()
            reader = csv.DictReader(content)
            for it in reader:
                rows.append({
                    'title': (it.get('title') or it.get('职位') or '').strip(),
                    'company': (it.get('company') or it.get('公司') or '').strip(),
                    'location': (it.get('location') or it.get('城市') or '').strip(),
                    'salary': (it.get('salary') or it.get('薪资') or '').strip(),
                    'source': it.get('source') or 'import',
                    'crawl_time': it.get('crawl_time') or datetime.now().isoformat()
                })
        else:
            return jsonify({'success': False, 'message': '仅支持JSON或CSV文件'}), 400

        # 过滤空标题
        rows = [r for r in rows if r.get('title')]
        if not rows:
            return jsonify({'success': False, 'message': '未解析到有效数据'}), 400

        path = _save_json(rows, 'jobs_import')
        _log(f"import file saved {path} count={len(rows)}")
        return jsonify({'success': True, 'message': '导入成功', 'data': {'count': len(rows), 'file': os.path.basename(path)}})
    except Exception as e:
        _log(f"import error {e}")
        return jsonify({'success': False, 'message': f'导入失败: {e}'}), 500


@job_bp.route('/api/job/data/sample', methods=['GET'])
def sample_job_data():
    """提供示例数据，便于快速演示"""
    sample = [
        { 'title': '护工/照护员', 'company': '安心养老服务中心', 'location': '北京', 'salary': '6k-8k/月', 'source': 'sample', 'crawl_time': datetime.now().isoformat() },
        { 'title': '医院陪护', 'company': '康复护理机构', 'location': '上海', 'salary': '180-220/天', 'source': 'sample', 'crawl_time': datetime.now().isoformat() },
        { 'title': '居家护理', 'company': '颐养家政', 'location': '广州', 'salary': '7k-9k/月', 'source': 'sample', 'crawl_time': datetime.now().isoformat() },
        { 'title': '老年护理员', 'company': '善护养老', 'location': '深圳', 'salary': '6.5k-8.5k/月', 'source': 'sample', 'crawl_time': datetime.now().isoformat() }
    ]
    return jsonify({'success': True, 'data': sample})

@job_bp.route('/api/job/data/sample/csv', methods=['GET'])
def sample_job_data_csv():
    """下载CSV示例模板（含示例数据）"""
    rows = [
        { 'title': '护工/照护员', 'company': '安心养老服务中心', 'location': '北京', 'salary': '6000-8000/月' },
        { 'title': '医院陪护', 'company': '康复护理机构', 'location': '上海', 'salary': '180-220/天' },
        { 'title': '居家护理', 'company': '颐养家政', 'location': '广州', 'salary': '7000-9000/月' },
        { 'title': '老年护理员', 'company': '善护养老', 'location': '深圳', 'salary': '6500-8500/月' }
    ]
    header = ['title','company','location','salary']
    def generate():
        yield ','.join(header) + '\n'
        for r in rows:
            yield ','.join([str(r.get(h,'')).replace(',', '，') for h in header]) + '\n'
    return Response(generate(), mimetype='text/csv', headers={
        'Content-Disposition': 'attachment; filename=sample_jobs.csv'
    })


@job_bp.route('/api/job/data/load-5000', methods=['POST'])
def load_5000_data():
    """加载5000条生成的护工数据"""
    try:
        # 优先查找50000条数据文件，如果不存在则查找5000条数据文件
        data_file_50000 = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'caregiver_jobs_50000.csv')
        data_file_5000 = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'caregiver_jobs_5000.csv')
        
        if os.path.exists(data_file_50000):
            data_file = data_file_50000
            data_type = "50000条"
        elif os.path.exists(data_file_5000):
            data_file = data_file_5000
            data_type = "5000条"
        else:
            return jsonify({'success': False, 'message': '数据文件不存在'}), 404
        
        # 读取CSV文件
        rows: List[Dict[str, Any]] = []
        with open(data_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 标准化数据格式
                rows.append({
                    'title': (row.get('title') or '').strip(),
                    'company': (row.get('company') or '').strip(),
                    'location': (row.get('city') or '').strip(),
                    'salary': (row.get('salary') or '').strip(),
                    'source': row.get('source') or 'generated',
                    'crawl_time': row.get('publish_date') or datetime.now().isoformat(),
                    'skills': (row.get('skills') or '').strip(),
                    'benefits': (row.get('benefits') or '').strip(),
                    'education': (row.get('education') or '').strip(),
                    'experience': (row.get('experience') or '').strip(),
                    'job_type': (row.get('job_type') or '').strip(),
                    'description': (row.get('description') or '').strip(),
                    'requirements': (row.get('requirements') or '').strip()
                })
        
        # 过滤空标题
        rows = [r for r in rows if r.get('title')]
        if not rows:
            return jsonify({'success': False, 'message': '未解析到有效数据'}), 400
        
        # 保存为JSON格式供系统使用
        path = _save_json(rows, 'jobs_5000')
        _log(f"loaded 5000 data saved {path} count={len(rows)}")
        
        return jsonify({
            'success': True, 
            'message': f'成功加载{len(rows)}条数据（{data_type}）', 
            'data': {
                'count': len(rows),
                'file': os.path.basename(path),
                'cities': len(set(r.get('location', '') for r in rows if r.get('location'))),
                'companies': len(set(r.get('company', '') for r in rows if r.get('company'))),
                'data_type': data_type
            }
        })
    except Exception as e:
        _log(f"load 5000 data error {e}")
        return jsonify({'success': False, 'message': f'加载失败: {e}'}), 500


@job_bp.route('/api/job/data/load-50000', methods=['POST'])
def load_50000_data():
    """加载50000条生成的护工数据"""
    try:
        # 查找50000条数据文件
        data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'caregiver_jobs_50000.csv')
        if not os.path.exists(data_file):
            return jsonify({'success': False, 'message': '50000条数据文件不存在'}), 404
        
        # 读取CSV文件
        rows: List[Dict[str, Any]] = []
        with open(data_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 标准化数据格式
                rows.append({
                    'title': (row.get('title') or '').strip(),
                    'company': (row.get('company') or '').strip(),
                    'location': (row.get('city') or '').strip(),
                    'salary': (row.get('salary') or '').strip(),
                    'source': row.get('source') or 'generated',
                    'crawl_time': row.get('publish_date') or datetime.now().isoformat(),
                    'skills': (row.get('skills') or '').strip(),
                    'benefits': (row.get('benefits') or '').strip(),
                    'education': (row.get('education') or '').strip(),
                    'experience': (row.get('experience') or '').strip(),
                    'job_type': (row.get('job_type') or '').strip(),
                    'description': (row.get('description') or '').strip(),
                    'requirements': (row.get('requirements') or '').strip()
                })
        
        # 过滤空标题
        rows = [r for r in rows if r.get('title')]
        if not rows:
            return jsonify({'success': False, 'message': '未解析到有效数据'}), 400
        
        # 保存为JSON格式供系统使用
        path = _save_json(rows, 'jobs_50000')
        _log(f"loaded 50000 data saved {path} count={len(rows)}")
        
        return jsonify({
            'success': True, 
            'message': f'成功加载{len(rows)}条数据（50000条）', 
            'data': {
                'count': len(rows),
                'file': os.path.basename(path),
                'cities': len(set(r.get('location', '') for r in rows if r.get('location'))),
                'companies': len(set(r.get('company', '') for r in rows if r.get('company'))),
                'data_type': '50000条'
            }
        })
    except Exception as e:
        _log(f"load 50000 data error {e}")
        return jsonify({'success': False, 'message': f'加载失败: {e}'}), 500


