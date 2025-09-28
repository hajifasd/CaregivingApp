#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
护工招聘数据生成器
生成5000条真实的护工招聘数据用于测试和演示
"""

import csv
import random
import json
from datetime import datetime, timedelta
from faker import Faker
import os

# 初始化Faker，使用中文
fake = Faker('zh_CN')

class CaregiverDataGenerator:
    def __init__(self):
        # 护工相关职位
        self.job_titles = [
            "护工", "护理员", "养老护理员", "康复护理员", "医疗护理员",
            "家庭护理员", "病患护理员", "老年护理员", "残疾人护理员",
            "术后护理员", "重症护理员", "居家护理员", "医院护理员",
            "护理助理", "护理师", "专业护理员", "高级护理员"
        ]
        
        # 技能要求
        self.skills = [
            "基础护理", "生活护理", "医疗护理", "康复护理", "心理护理",
            "急救技能", "按摩技能", "营养配餐", "药物管理", "血压测量",
            "血糖监测", "伤口护理", "导尿护理", "鼻饲护理", "吸痰护理",
            "翻身护理", "体位护理", "安全防护", "沟通技巧", "耐心细心",
            "责任心强", "吃苦耐劳", "身体健康", "无传染病", "有爱心"
        ]
        
        # 工作地点
        self.cities = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "苏州", "成都",
            "重庆", "武汉", "西安", "天津", "青岛", "大连", "厦门", "福州",
            "长沙", "郑州", "济南", "沈阳", "哈尔滨", "长春", "石家庄",
            "太原", "呼和浩特", "兰州", "西宁", "银川", "乌鲁木齐", "昆明",
            "贵阳", "南宁", "海口", "南昌", "合肥", "温州", "无锡", "常州"
        ]
        
        # 公司类型
        self.company_types = [
            "医疗护理公司", "养老院", "康复中心", "家政服务公司", "医院",
            "社区卫生服务中心", "护理站", "健康管理公司", "医疗科技公司",
            "养老服务公司", "专业护理机构", "医疗集团", "健康产业公司"
        ]
        
        # 学历要求
        self.education_levels = [
            "不限", "初中", "高中", "中专", "大专", "本科", "护理专业优先"
        ]
        
        # 工作经验要求
        self.experience_levels = [
            "不限", "1年以下", "1-3年", "3-5年", "5-10年", "10年以上"
        ]
        
        # 工作性质
        self.job_types = [
            "全职", "兼职", "实习", "临时", "长期", "短期", "夜班", "白班"
        ]
        
        # 薪资范围（元/月）
        self.salary_ranges = [
            (2000, 3000), (3000, 4000), (4000, 5000), (5000, 6000),
            (6000, 8000), (8000, 10000), (10000, 12000), (12000, 15000),
            (15000, 20000), (20000, 25000), (25000, 30000)
        ]
        
        # 福利待遇
        self.benefits = [
            "五险一金", "包吃包住", "带薪年假", "节日福利", "生日福利",
            "培训机会", "晋升空间", "加班费", "交通补贴", "餐补",
            "住宿补贴", "健康体检", "意外保险", "年终奖", "绩效奖金"
        ]

    def generate_salary(self):
        """生成薪资信息"""
        salary_range = random.choice(self.salary_ranges)
        min_salary, max_salary = salary_range
        
        # 随机生成具体薪资
        if random.random() < 0.3:  # 30%概率生成具体数字
            salary = random.randint(min_salary, max_salary)
            return f"{salary}元/月"
        else:  # 70%概率生成范围
            return f"{min_salary}-{max_salary}元/月"

    def generate_skills(self):
        """生成技能要求"""
        num_skills = random.randint(3, 8)
        selected_skills = random.sample(self.skills, num_skills)
        return "、".join(selected_skills)

    def generate_benefits(self):
        """生成福利待遇"""
        num_benefits = random.randint(2, 6)
        selected_benefits = random.sample(self.benefits, num_benefits)
        return "、".join(selected_benefits)

    def generate_job_description(self, title, company, city):
        """生成职位描述"""
        descriptions = [
            f"负责{title}工作，为患者提供专业的护理服务，确保患者安全和舒适。",
            f"在{company}担任{title}，负责日常护理工作，具备良好的沟通能力和责任心。",
            f"为{title}岗位，主要工作内容包括生活护理、医疗护理等，要求有相关经验。",
            f"招聘{title}，工作地点在{city}，要求身体健康，有爱心，能吃苦耐劳。",
            f"需要{title}，负责照顾患者日常生活，协助医疗护理，提供专业服务。"
        ]
        return random.choice(descriptions)

    def generate_requirements(self):
        """生成任职要求"""
        requirements = [
            f"学历要求：{random.choice(self.education_levels)}",
            f"工作经验：{random.choice(self.experience_levels)}",
            f"年龄要求：{random.randint(18, 60)}岁以下",
            f"性别要求：{random.choice(['不限', '男', '女'])}",
            f"技能要求：{self.generate_skills()}",
            f"其他要求：身体健康，无传染病史，有爱心和责任心"
        ]
        return "；".join(random.sample(requirements, random.randint(3, 6)))

    def generate_contact_info(self):
        """生成联系方式"""
        return {
            "contact_person": fake.name(),
            "phone": fake.phone_number(),
            "email": fake.email(),
            "address": fake.address()
        }

    def generate_single_job(self, job_id):
        """生成单条招聘数据"""
        title = random.choice(self.job_titles)
        city = random.choice(self.cities)
        company = f"{random.choice(self.company_types)}{random.randint(1, 999)}"
        
        # 生成发布时间（最近30天内）
        publish_date = fake.date_between(start_date='-30d', end_date='today')
        
        # 生成联系信息
        contact = self.generate_contact_info()
        
        job_data = {
            "id": job_id,
            "title": title,
            "company": company,
            "city": city,
            "salary": self.generate_salary(),
            "education": random.choice(self.education_levels),
            "experience": random.choice(self.experience_levels),
            "job_type": random.choice(self.job_types),
            "skills": self.generate_skills(),
            "benefits": self.generate_benefits(),
            "description": self.generate_job_description(title, company, city),
            "requirements": self.generate_requirements(),
            "publish_date": publish_date.strftime("%Y-%m-%d"),
            "contact_person": contact["contact_person"],
            "phone": contact["phone"],
            "email": contact["email"],
            "address": contact["address"],
            "source": random.choice(["51job", "智联招聘", "Boss直聘", "拉勾网", "猎聘网"]),
            "status": random.choice(["招聘中", "已暂停", "已结束"]),
            "views": random.randint(10, 1000),
            "applications": random.randint(0, 50)
        }
        
        return job_data

    def generate_data(self, count=50000):
        """生成指定数量的数据"""
        print(f"开始生成{count}条护工招聘数据...")
        
        data = []
        for i in range(1, count + 1):
            if i % 1000 == 0:  # 每1000条显示一次进度
                print(f"已生成 {i} 条数据... ({i/count*100:.1f}%)")
            data.append(self.generate_single_job(i))
        
        print(f"数据生成完成！共生成 {len(data)} 条数据")
        return data

    def save_to_csv(self, data, filename="caregiver_jobs_50000.csv"):
        """保存数据到CSV文件"""
        if not data:
            print("没有数据可保存")
            return
        
        # 确保目录存在
        dirname = os.path.dirname(filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        
        # CSV字段
        fieldnames = [
            "id", "title", "company", "city", "salary", "education", 
            "experience", "job_type", "skills", "benefits", "description",
            "requirements", "publish_date", "contact_person", "phone",
            "email", "address", "source", "status", "views", "applications"
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"数据已保存到: {filename}")

    def save_to_json(self, data, filename="caregiver_jobs_50000.json"):
        """保存数据到JSON文件"""
        if not data:
            print("没有数据可保存")
            return
        
        # 确保目录存在
        dirname = os.path.dirname(filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到: {filename}")

def main():
    """主函数"""
    print("护工招聘数据生成器")
    print("=" * 50)
    
    # 创建生成器
    generator = CaregiverDataGenerator()
    
    # 生成50000条数据
    data = generator.generate_data(50000)
    
    # 保存为CSV和JSON格式
    generator.save_to_csv(data, "caregiver_jobs_50000.csv")
    generator.save_to_json(data, "caregiver_jobs_50000.json")
    
    # 显示统计信息
    print("\n数据统计:")
    print(f"总数据量: {len(data)}")
    print(f"涉及城市: {len(set(job['city'] for job in data))}")
    print(f"职位类型: {len(set(job['title'] for job in data))}")
    print(f"公司数量: {len(set(job['company'] for job in data))}")
    
    # 薪资分布统计
    salary_ranges = {}
    for job in data:
        salary = job['salary']
        if '元/月' in salary:
            salary = salary.replace('元/月', '')
            if '-' in salary:
                min_sal, max_sal = salary.split('-')
                avg_sal = (int(min_sal) + int(max_sal)) // 2
            else:
                avg_sal = int(salary)
            
            if avg_sal < 3000:
                range_key = "2000-3000"
            elif avg_sal < 5000:
                range_key = "3000-5000"
            elif avg_sal < 8000:
                range_key = "5000-8000"
            elif avg_sal < 12000:
                range_key = "8000-12000"
            else:
                range_key = "12000+"
            
            salary_ranges[range_key] = salary_ranges.get(range_key, 0) + 1
    
    print("\n薪资分布:")
    for range_key, count in sorted(salary_ranges.items()):
        print(f"  {range_key}元/月: {count}条")

if __name__ == "__main__":
    main()
