"""
护工资源管理系统 - 工作机会管理服务
====================================

处理工作机会相关的业务逻辑，包括工作机会查询、申请、管理等
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from decimal import Decimal

class JobService:
    """工作机会管理服务"""
    
    def __init__(self, db=None):
        self.db = db
        self.job_model = None
        self.application_model = None
    
    def set_db(self, db):
        """设置数据库连接"""
        self.db = db
        from models.business import JobData
        from models.employment_contract import ContractApplication
        self.job_model = JobData.get_model(db)
        self.application_model = ContractApplication.get_model(db)
    
    def get_available_jobs(self, page: int = 1, per_page: int = 10, 
                         location: str = '', job_type: str = '') -> Dict[str, Any]:
        """获取可申请的工作机会列表"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 构建查询
            query = self.job_model.query.filter(
                self.job_model.job_name.isnot(None),
                self.job_model.job_name != ''
            )
            
            # 根据位置筛选
            if location:
                query = query.filter(self.job_model.city.contains(location))
            
            # 根据工作类型筛选
            if job_type:
                query = query.filter(self.job_model.job_name.contains(job_type))
            
            # 分页查询
            total = query.count()
            jobs = query.order_by(self.job_model.crawl_time.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 转换为前端需要的格式
            job_list = []
            for job in jobs.items:
                job_dict = {
                    'id': job.id,
                    'title': job.job_name or '未知职位',
                    'description': f"公司：{job.company or '未知公司'}",
                    'location': job.city or '未知地点',
                    'salary': self._format_salary(job.salary_low, job.salary_high),
                    'job_type': self._determine_job_type(job.job_name),
                    'schedule': '工作时间面议',
                    'requirements': job.experience or '经验不限',
                    'benefits': '福利待遇面议',
                    'company': job.company or '未知公司',
                    'publish_date': job.crawl_time.strftime('%Y-%m-%d') if job.crawl_time else '未知',
                    'skills': job.skills or '',
                    'education': job.education or '学历不限'
                }
                job_list.append(job_dict)
            
            return {
                "success": True,
                "data": job_list,
                "total": total,
                "page": page,
                "per_page": per_page
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取工作机会失败: {str(e)}"}
    
    def get_job_detail(self, job_id: int) -> Dict[str, Any]:
        """获取工作机会详情"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            job = self.job_model.query.get(job_id)
            if not job:
                return {"success": False, "message": "工作机会不存在"}
            
            job_dict = {
                'id': job.id,
                'title': job.job_name or '未知职位',
                'description': f"公司：{job.company or '未知公司'}\n技能要求：{job.skills or '无特殊要求'}\n学历要求：{job.education or '不限'}",
                'location': job.city or '未知地点',
                'salary': self._format_salary(job.salary_low, job.salary_high),
                'job_type': self._determine_job_type(job.job_name),
                'schedule': '工作时间面议',
                'requirements': job.experience or '经验不限',
                'benefits': '福利待遇面议',
                'company': job.company or '未知公司',
                'publish_date': job.crawl_time.strftime('%Y-%m-%d') if job.crawl_time else '未知',
                'skills': job.skills or '',
                'education': job.education or '学历不限',
                'salary_low': job.salary_low,
                'salary_high': job.salary_high
            }
            
            return {
                "success": True,
                "data": job_dict
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取工作详情失败: {str(e)}"}
    
    def apply_for_job(self, job_id: int, caregiver_id: int, 
                     application_message: str = '') -> Dict[str, Any]:
        """申请工作机会"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 检查工作机会是否存在
            job = self.job_model.query.get(job_id)
            if not job:
                return {"success": False, "message": "工作机会不存在"}
            
            # 检查是否已经申请过（这里需要根据实际业务逻辑调整）
            # 由于ContractApplication模型是用于用户向护工申请，不是护工申请工作
            # 我们需要创建一个新的申请记录或者使用不同的逻辑
            
            # 创建申请记录（这里需要根据实际需求调整字段）
            application = self.application_model(
                user_id=0,  # 这里需要根据实际业务逻辑调整
                caregiver_id=caregiver_id,
                service_type='工作申请',
                proposed_start_date=datetime.now().date(),
                application_message=application_message,
                status='pending'
            )
            
            self.db.session.add(application)
            self.db.session.commit()
            
            return {
                "success": True,
                "message": "申请已提交，请等待审核",
                "data": application.to_dict()
            }
            
        except Exception as e:
            self.db.session.rollback()
            return {"success": False, "message": f"申请工作失败: {str(e)}"}
    
    def get_caregiver_applications(self, caregiver_id: int, 
                                 page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """获取护工的工作申请列表"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 查询护工的申请记录
            query = self.application_model.query.filter_by(caregiver_id=caregiver_id)
            total = query.count()
            applications = query.order_by(self.application_model.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 转换为前端需要的格式
            application_list = []
            for app in applications.items:
                app_dict = {
                    'id': app.id,
                    'job_title': f"服务申请 - {app.service_type}",
                    'job_description': f"服务类型：{app.service_type}",
                    'job_location': '工作地点待定',
                    'job_salary': f"建议时薪：{app.proposed_rate}元/小时" if app.proposed_rate else '面议',
                    'job_type': '服务申请',
                    'job_schedule': f"建议开始：{app.proposed_start_date}",
                    'status': app.status,
                    'applied_date': app.created_at.strftime('%Y-%m-%d') if app.created_at else '未知',
                    'review_notes': app.caregiver_response or '',
                    'application_message': app.application_message or ''
                }
                application_list.append(app_dict)
            
            return {
                "success": True,
                "data": application_list,
                "total": total,
                "page": page,
                "per_page": per_page
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取工作申请失败: {str(e)}"}
    
    def cancel_application(self, application_id: int, caregiver_id: int) -> Dict[str, Any]:
        """取消工作申请"""
        try:
            if not self.db:
                return {"success": False, "message": "数据库连接未初始化"}
            
            # 查找申请记录
            application = self.application_model.query.filter_by(
                id=application_id,
                caregiver_id=caregiver_id
            ).first()
            
            if not application:
                return {"success": False, "message": "申请记录不存在"}
            
            if application.status != 'pending':
                return {"success": False, "message": "只能取消待审核的申请"}
            
            # 更新状态为已取消
            application.status = 'withdrawn'  # 使用withdrawn状态表示护工主动取消
            
            self.db.session.commit()
            
            return {
                "success": True,
                "message": "申请已取消"
            }
            
        except Exception as e:
            self.db.session.rollback()
            return {"success": False, "message": f"取消申请失败: {str(e)}"}
    
    def _format_salary(self, salary_low: Optional[int], salary_high: Optional[int]) -> str:
        """格式化薪资显示"""
        if salary_low and salary_high:
            return f"{salary_low}-{salary_high}元/月"
        elif salary_low:
            return f"{salary_low}元/月起"
        elif salary_high:
            return f"最高{salary_high}元/月"
        else:
            return "面议"
    
    def _determine_job_type(self, job_name: Optional[str]) -> str:
        """根据职位名称确定工作类型"""
        if not job_name:
            return "未知"
        
        job_name_lower = job_name.lower()
        if any(keyword in job_name_lower for keyword in ['兼职', 'part-time', '临时']):
            return "兼职"
        elif any(keyword in job_name_lower for keyword in ['全职', 'full-time', '长期']):
            return "全职"
        elif any(keyword in job_name_lower for keyword in ['灵活', 'flexible', '自由']):
            return "灵活"
        else:
            return "全职"
