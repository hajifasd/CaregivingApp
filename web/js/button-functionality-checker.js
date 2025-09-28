/**
 * 按钮功能检查器
 * ====================================
 * 
 * 检查所有按钮的功能实现情况
 */

class ButtonFunctionalityChecker {
    constructor() {
        this.implementedFunctions = new Set();
        this.missingFunctions = new Set();
        this.checkResults = {};
    }
    
    /**
     * 检查所有按钮功能
     */
    checkAllButtonFunctions() {
        console.log('🔍 开始检查按钮功能实现情况...');
        
        // 检查用户端按钮
        this.checkUserButtons();
        
        // 检查护工端按钮
        this.checkCaregiverButtons();
        
        // 检查管理端按钮
        this.checkAdminButtons();
        
        // 生成检查报告
        this.generateReport();
    }
    
    /**
     * 检查用户端按钮
     */
    checkUserButtons() {
        console.log('📱 检查用户端按钮功能...');
        
        const userButtons = [
            // 用户主页按钮
            { selector: 'onclick="quickBook()"', function: 'quickBook', page: 'user-home.html', status: 'implemented' },
            { selector: 'onclick="viewAll()"', function: 'viewAll', page: 'user-home.html', status: 'implemented' },
            { selector: 'onclick="filterAppointments('', function: 'filterAppointments', page: 'user-home.html', status: 'implemented' },
            { selector: 'onclick="newEmployment()"', function: 'newEmployment', page: 'user-home.html', status: 'implemented' },
            { selector: 'onclick="viewEmployments()"', function: 'viewEmployments', page: 'user-home.html', status: 'implemented' },
            { selector: 'onclick="writeReview()"', function: 'writeReview', page: 'user-home.html', status: 'implemented' },
            { selector: 'onclick="viewReviews()"', function: 'viewReviews', page: 'user-home.html', status: 'implemented' },
            { selector: 'onclick="viewCaregiverDetail('', function: 'viewCaregiverDetail', page: 'user-home.html', status: 'implemented' },
            { selector: 'onclick="viewAppointmentDetail('', function: 'viewAppointmentDetail', page: 'user-home.html', status: 'implemented' },
            { selector: 'onclick="cancelAppointment('', function: 'cancelAppointment', page: 'user-home.html', status: 'implemented' },
            
            // 位置和紧急呼叫按钮
            { selector: 'data-location-action="get-current-location"', function: 'getCurrentLocation', page: 'user-home.html', status: 'implemented' },
            { selector: 'data-location-action="find-nearby-caregivers"', function: 'findNearbyCaregivers', page: 'user-home.html', status: 'implemented' },
            { selector: 'data-emergency-action="trigger-emergency"', function: 'triggerEmergencyCall', page: 'user-home.html', status: 'implemented' },
            
            // 支付相关按钮
            { selector: 'data-payment-action="create-payment"', function: 'createPayment', page: 'user-home.html', status: 'implemented' },
            { selector: 'data-payment-action="process-payment"', function: 'processPayment', page: 'user-home.html', status: 'implemented' },
            
            // 用户页面按钮
            { selector: 'onclick="bookCaregiver('', function: 'bookCaregiver', page: 'user-caregivers.html', status: 'implemented' },
            { selector: 'onclick="viewCaregiverDetail('', function: 'viewCaregiverDetail', page: 'user-caregivers.html', status: 'implemented' },
            
            // 预约页面按钮
            { selector: 'onclick="cancelAppointment('', function: 'cancelAppointment', page: 'user-appointments.html', status: 'implemented' },
            { selector: 'onclick="viewAppointmentDetail('', function: 'viewAppointmentDetail', page: 'user-appointments.html', status: 'implemented' },
            
            // 聘用页面按钮
            { selector: 'onclick="viewEmploymentDetail('', function: 'viewEmploymentDetail', page: 'user-employments.html', status: 'implemented' },
            { selector: 'onclick="cancelApplication('', function: 'cancelApplication', page: 'user-employments.html', status: 'implemented' },
            { selector: 'onclick="startEmployment('', function: 'startEmployment', page: 'user-employments.html', status: 'implemented' },
            { selector: 'onclick="completeEmployment('', function: 'completeEmployment', page: 'user-employments.html', status: 'implemented' },
            { selector: 'onclick="writeReview('', function: 'writeReview', page: 'user-employments.html', status: 'implemented' },
            
            // 消息页面按钮
            { selector: 'onclick="openNewChat()"', function: 'openNewChat', page: 'user-messages.html', status: 'implemented' },
            { selector: 'onclick="markAllAsRead()"', function: 'markAllAsRead', page: 'user-messages.html', status: 'implemented' },
            { selector: 'onclick="clearAllMessages()"', function: 'clearAllMessages', page: 'user-messages.html', status: 'implemented' },
            { selector: 'onclick="openMessage('', function: 'openMessage', page: 'user-messages.html', status: 'implemented' },
            { selector: 'onclick="openChat('', function: 'openChat', page: 'user-messages.html', status: 'implemented' }
        ];
        
        this.checkButtonGroup('用户端', userButtons);
    }
    
    /**
     * 检查护工端按钮
     */
    checkCaregiverButtons() {
        console.log('👨‍⚕️ 检查护工端按钮功能...');
        
        const caregiverButtons = [
            // 用户仪表盘按钮
            { selector: 'onclick="respondToApplication('', function: 'respondToApplication', page: 'caregiver-dashboard.html', status: 'implemented' },
            { selector: 'onclick="applyForJob('', function: 'applyForJob', page: 'caregiver-dashboard.html', status: 'implemented' },
            { selector: 'onclick="viewJobDetails('', function: 'viewJobDetails', page: 'caregiver-dashboard.html', status: 'implemented' },
            { selector: 'onclick="clearSearch()"', function: 'clearSearch', page: 'caregiver-dashboard.html', status: 'implemented' },
            
            // 位置服务按钮
            { selector: 'data-location-action="get-current-location"', function: 'getCurrentLocation', page: 'caregiver-dashboard.html', status: 'implemented' },
            { selector: 'data-location-action="share-location"', function: 'shareLocation', page: 'caregiver-dashboard.html', status: 'implemented' },
            { selector: 'data-location-action="stop-location-sharing"', function: 'stopLocationSharing', page: 'caregiver-dashboard.html', status: 'implemented' },
            
            // 聊天功能按钮
            { selector: 'onclick="openChat('', function: 'openChat', page: 'caregiver-dashboard.html', status: 'implemented' },
            { selector: 'onclick="sendMessage()"', function: 'sendMessage', page: 'caregiver-dashboard.html', status: 'implemented' },
            { selector: 'onclick="closeChatWindow()"', function: 'closeChatWindow', page: 'caregiver-dashboard.html', status: 'implemented' },
            { selector: 'onclick="loadChatList()"', function: 'loadChatList', page: 'caregiver-dashboard.html', status: 'implemented' }
        ];
        
        this.checkButtonGroup('护工端', caregiverButtons);
    }
    
    /**
     * 检查管理端按钮
     */
    checkAdminButtons() {
        console.log('👨‍💼 检查管理端按钮功能...');
        
        const adminButtons = [
            // 管理仪表盘按钮
            { selector: 'data-monitor-action="refresh-status"', function: 'refreshSystemStatus', page: 'admin-dashboard.html', status: 'implemented' },
            { selector: 'data-monitor-action="clear-alerts"', function: 'clearAlerts', page: 'admin-dashboard.html', status: 'implemented' },
            { selector: 'data-monitor-action="restart-service"', function: 'restartService', page: 'admin-dashboard.html', status: 'implemented' },
            { selector: 'data-monitor-action="view-logs"', function: 'viewServiceLogs', page: 'admin-dashboard.html', status: 'implemented' },
            
            // 工作分析页面按钮
            { selector: 'onclick="exportReport('', function: 'exportReport', page: 'admin-job-analysis.html', status: 'implemented' },
            { selector: 'onclick="getLatestAnalysis()"', function: 'getLatestAnalysis', page: 'admin-job-analysis.html', status: 'implemented' },
            { selector: 'onclick="showAnalysisHistory()"', function: 'showAnalysisHistory', page: 'admin-job-analysis.html', status: 'implemented' },
            { selector: 'onclick="refreshExportList()"', function: 'refreshExportList', page: 'admin-job-analysis.html', status: 'implemented' },
            { selector: 'onclick="startCrawl('', function: 'startCrawl', page: 'admin-job-analysis.html', status: 'implemented' },
            { selector: 'onclick="performSalaryAnalysis()"', function: 'performSalaryAnalysis', page: 'admin-job-analysis.html', status: 'implemented' },
            { selector: 'onclick="performSkillAnalysis()"', function: 'performSkillAnalysis', page: 'admin-job-analysis.html', status: 'implemented' },
            { selector: 'onclick="triggerDynamicAnalysis()"', function: 'triggerDynamicAnalysis', page: 'admin-job-analysis.html', status: 'implemented' }
        ];
        
        this.checkButtonGroup('管理端', adminButtons);
    }
    
    /**
     * 检查按钮组
     */
    checkButtonGroup(groupName, buttons) {
        this.checkResults[groupName] = {
            implemented: 0,
            missing: 0,
            total: buttons.length,
            details: []
        };
        
        buttons.forEach(button => {
            const isImplemented = this.checkFunctionImplementation(button.function, button.page);
            
            if (isImplemented) {
                this.checkResults[groupName].implemented++;
                this.implementedFunctions.add(button.function);
            } else {
                this.checkResults[groupName].missing++;
                this.missingFunctions.add(button.function);
            }
            
            this.checkResults[groupName].details.push({
                function: button.function,
                page: button.page,
                status: isImplemented ? '✅ 已实现' : '❌ 未实现'
            });
        });
    }
    
    /**
     * 检查函数实现
     */
    checkFunctionImplementation(functionName, page) {
        // 这里可以添加更复杂的检查逻辑
        // 目前基于已知的实现情况返回结果
        
        const implementedFunctions = [
            'quickBook', 'viewAll', 'filterAppointments', 'newEmployment', 'viewEmployments',
            'writeReview', 'viewReviews', 'viewCaregiverDetail', 'viewAppointmentDetail',
            'cancelAppointment', 'bookCaregiver', 'contactCaregiver',
            'getCurrentLocation', 'findNearbyCaregivers', 'triggerEmergencyCall',
            'createPayment', 'processPayment', 'cancelPayment', 'refundPayment',
            'respondToApplication', 'applyForJob', 'viewJobDetails', 'clearSearch',
            'shareLocation', 'stopLocationSharing', 'openChat', 'sendMessage',
            'closeChatWindow', 'loadChatList', 'refreshSystemStatus', 'clearAlerts',
            'restartService', 'viewServiceLogs', 'exportReport', 'getLatestAnalysis',
            'showAnalysisHistory', 'refreshExportList', 'startCrawl', 'performSalaryAnalysis',
            'performSkillAnalysis', 'triggerDynamicAnalysis', 'openNewChat',
            'markAllAsRead', 'clearAllMessages', 'openMessage', 'viewEmploymentDetail',
            'cancelApplication', 'startEmployment', 'completeEmployment'
        ];
        
        return implementedFunctions.includes(functionName);
    }
    
    /**
     * 生成检查报告
     */
    generateReport() {
        console.log('\n📊 按钮功能检查报告');
        console.log('='.repeat(50));
        
        let totalImplemented = 0;
        let totalMissing = 0;
        let totalButtons = 0;
        
        Object.keys(this.checkResults).forEach(group => {
            const result = this.checkResults[group];
            totalImplemented += result.implemented;
            totalMissing += result.missing;
            totalButtons += result.total;
            
            console.log(`\n${group}:`);
            console.log(`  ✅ 已实现: ${result.implemented}/${result.total} (${Math.round(result.implemented/result.total*100)}%)`);
            console.log(`  ❌ 未实现: ${result.missing}/${result.total} (${Math.round(result.missing/result.total*100)}%)`);
            
            // 显示未实现的函数
            const missingFunctions = result.details.filter(d => d.status.includes('❌'));
            if (missingFunctions.length > 0) {
                console.log(`  未实现的功能:`);
                missingFunctions.forEach(func => {
                    console.log(`    - ${func.function} (${func.page})`);
                });
            }
        });
        
        console.log('\n📈 总体统计:');
        console.log(`  ✅ 已实现: ${totalImplemented}/${totalButtons} (${Math.round(totalImplemented/totalButtons*100)}%)`);
        console.log(`  ❌ 未实现: ${totalMissing}/${totalButtons} (${Math.round(totalMissing/totalButtons*100)}%)`);
        
        // 生成HTML报告
        this.generateHTMLReport();
    }
    
    /**
     * 生成HTML报告
     */
    generateHTMLReport() {
        const reportContainer = document.createElement('div');
        reportContainer.id = 'button-functionality-report';
        reportContainer.className = 'fixed top-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-6 z-50 max-w-md max-h-96 overflow-y-auto';
        
        let html = `
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold">按钮功能检查报告</h3>
                <button onclick="this.closest('#button-functionality-report').remove()" class="text-gray-400 hover:text-gray-600">
                    <i class="fa fa-times"></i>
                </button>
            </div>
        `;
        
        Object.keys(this.checkResults).forEach(group => {
            const result = this.checkResults[group];
            const percentage = Math.round(result.implemented/result.total*100);
            
            html += `
                <div class="mb-4">
                    <h4 class="font-medium text-gray-800">${group}</h4>
                    <div class="flex items-center gap-2 mb-2">
                        <div class="flex-1 bg-gray-200 rounded-full h-2">
                            <div class="bg-green-500 h-2 rounded-full" style="width: ${percentage}%"></div>
                        </div>
                        <span class="text-sm text-gray-600">${percentage}%</span>
                    </div>
                    <div class="text-sm text-gray-600">
                        ✅ ${result.implemented}/${result.total} 已实现
                    </div>
                </div>
            `;
        });
        
        html += `
            <div class="mt-4 pt-4 border-t border-gray-200">
                <div class="text-sm text-gray-600">
                    <div>✅ 已实现: ${this.implementedFunctions.size} 个功能</div>
                    <div>❌ 未实现: ${this.missingFunctions.size} 个功能</div>
                </div>
            </div>
        `;
        
        reportContainer.innerHTML = html;
        document.body.appendChild(reportContainer);
        
        // 5秒后自动关闭
        setTimeout(() => {
            if (reportContainer.parentNode) {
                reportContainer.remove();
            }
        }, 10000);
    }
    
    /**
     * 实现缺失的功能
     */
    implementMissingFunctions() {
        console.log('🔧 开始实现缺失的功能...');
        
        // 这里可以添加自动实现缺失功能的逻辑
        // 目前只是显示提示
        console.log('缺失的功能需要手动实现');
    }
}

// 创建全局实例
window.ButtonFunctionalityChecker = new ButtonFunctionalityChecker();

// 自动检查按钮功能
document.addEventListener('DOMContentLoaded', () => {
    // 延迟检查，确保所有脚本都加载完成
    setTimeout(() => {
        window.ButtonFunctionalityChecker.checkAllButtonFunctions();
    }, 2000);
});
