"""
护工资源管理系统 - 文件上传API
====================================

支持用户头像、护工头像、文档等文件上传功能
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from utils.auth import require_auth
from utils.file_upload import allowed_file, generate_unique_filename, save_uploaded_file
import os
import logging

logger = logging.getLogger(__name__)
file_upload_bp = Blueprint('file_upload', __name__)

@file_upload_bp.route('/api/upload/avatar', methods=['POST'])
@require_auth()
def upload_avatar():
    """上传头像"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        # 检查文件格式
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': '不支持的文件格式，请上传图片文件'
            }), 400
        
        # 检查文件大小 (限制为5MB)
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置到文件开头
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({
                'success': False,
                'message': '文件大小不能超过5MB'
            }), 400
        
        # 生成安全的文件名
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename, 'avatar')
        
        # 设置上传目录
        upload_folder = os.path.join(current_app.root_path, '..', 'web', 'uploads', 'avatars')
        
        # 保存文件
        file_path = save_uploaded_file(file, upload_folder, unique_filename)
        
        if file_path:
            # 生成访问URL
            file_url = f"/uploads/avatars/{unique_filename}"
            
            return jsonify({
                'success': True,
                'data': {
                    'filename': unique_filename,
                    'original_filename': original_filename,
                    'file_path': file_path,
                    'file_url': file_url,
                    'file_size': file_size
                },
                'message': '头像上传成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '文件保存失败'
            }), 500
            
    except Exception as e:
        logger.error(f"头像上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'头像上传失败: {str(e)}'
        }), 500

@file_upload_bp.route('/api/upload/document', methods=['POST'])
@require_auth()
def upload_document():
    """上传文档"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        # 检查文件格式 (允许更多文档格式)
        allowed_doc_extensions = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_doc_extensions:
            return jsonify({
                'success': False,
                'message': '不支持的文件格式，请上传PDF、Word文档或图片文件'
            }), 400
        
        # 检查文件大小 (限制为10MB)
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置到文件开头
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({
                'success': False,
                'message': '文件大小不能超过10MB'
            }), 400
        
        # 生成安全的文件名
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename, 'doc')
        
        # 设置上传目录
        upload_folder = os.path.join(current_app.root_path, '..', 'web', 'uploads', 'documents')
        
        # 保存文件
        file_path = save_uploaded_file(file, upload_folder, unique_filename)
        
        if file_path:
            # 生成访问URL
            file_url = f"/uploads/documents/{unique_filename}"
            
            return jsonify({
                'success': True,
                'data': {
                    'filename': unique_filename,
                    'original_filename': original_filename,
                    'file_path': file_path,
                    'file_url': file_url,
                    'file_size': file_size,
                    'file_type': file_ext
                },
                'message': '文档上传成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '文件保存失败'
            }), 500
            
    except Exception as e:
        logger.error(f"文档上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'文档上传失败: {str(e)}'
        }), 500

@file_upload_bp.route('/api/upload/chat-image', methods=['POST'])
@require_auth()
def upload_chat_image():
    """上传聊天图片"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        # 检查文件格式 (只允许图片)
        allowed_image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_image_extensions:
            return jsonify({
                'success': False,
                'message': '只支持图片格式：JPG、PNG、GIF、WebP'
            }), 400
        
        # 检查文件大小 (限制为3MB)
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置到文件开头
        
        if file_size > 3 * 1024 * 1024:  # 3MB
            return jsonify({
                'success': False,
                'message': '图片大小不能超过3MB'
            }), 400
        
        # 生成安全的文件名
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename, 'chat')
        
        # 设置上传目录
        upload_folder = os.path.join(current_app.root_path, '..', 'web', 'uploads', 'chat_images')
        
        # 保存文件
        file_path = save_uploaded_file(file, upload_folder, unique_filename)
        
        if file_path:
            # 生成访问URL
            file_url = f"/uploads/chat_images/{unique_filename}"
            
            return jsonify({
                'success': True,
                'data': {
                    'filename': unique_filename,
                    'original_filename': original_filename,
                    'file_path': file_path,
                    'file_url': file_url,
                    'file_size': file_size,
                    'file_type': file_ext
                },
                'message': '图片上传成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '文件保存失败'
            }), 500
            
    except Exception as e:
        logger.error(f"聊天图片上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'聊天图片上传失败: {str(e)}'
        }), 500

@file_upload_bp.route('/api/upload/delete', methods=['POST'])
@require_auth()
def delete_uploaded_file():
    """删除上传的文件"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({
                'success': False,
                'message': '缺少文件路径'
            }), 400
        
        # 安全检查：确保文件在允许的目录内
        allowed_dirs = ['avatars', 'documents', 'chat_images']
        if not any(allowed_dir in file_path for allowed_dir in allowed_dirs):
            return jsonify({
                'success': False,
                'message': '不允许删除此文件'
            }), 403
        
        # 删除文件
        from utils.file_upload import delete_file
        if delete_file(file_path):
            return jsonify({
                'success': True,
                'message': '文件删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '文件删除失败'
            }), 500
            
    except Exception as e:
        logger.error(f"文件删除失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'文件删除失败: {str(e)}'
        }), 500
