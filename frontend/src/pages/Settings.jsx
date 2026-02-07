import React, { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Save, Mail, Bell } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Settings = () => {
  const [email, setEmail] = useState('');
  const [alertThreshold, setAlertThreshold] = useState(70);
  const [enabled, setEnabled] = useState(true);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!email) {
      toast.error('请输入邮箱地址');
      return;
    }

    try {
      setSaving(true);
      await axios.post(`${API}/settings`, {
        email,
        alert_threshold: alertThreshold,
        enabled,
      });
      toast.success('设置已保存');
    } catch (error) {
      console.error('保存设置失败:', error);
      toast.error('保存失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 lg:p-8" data-testid="settings-page">
      <div className="mb-6">
        <h1 className="text-3xl font-heading font-bold text-white mb-2">设置</h1>
        <p className="text-sm text-gray-400">配置通知和预警设置</p>
      </div>

      <div className="max-w-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card rounded-sm p-6 mb-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-[#D4AF37]/10 rounded-sm">
              <Mail size={20} className="text-[#D4AF37]" />
            </div>
            <h2 className="text-lg font-heading font-bold text-white">邮件通知</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">邮箱地址</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="请输入您的邮箱"
                data-testid="email-input"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#D4AF37] transition-colors"
              />
              <p className="text-xs text-gray-500 mt-2">
                当产生明确的交易信号时，系统将发送邮件通知。
              </p>
            </div>

            <div className="flex items-center justify-between py-3 border-t border-white/10">
              <div>
                <p className="text-sm text-white mb-1">启用邮件通知</p>
                <p className="text-xs text-gray-500">接收交易信号的邮件提醒</p>
              </div>
              <button
                onClick={() => setEnabled(!enabled)}
                data-testid="enable-toggle"
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  enabled ? 'bg-[#D4AF37]' : 'bg-white/10'
                }`}
              >
                <span
                  className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                    enabled ? 'transform translate-x-6' : ''
                  }`}
                ></span>
              </button>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card rounded-sm p-6 mb-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-[#D4AF37]/10 rounded-sm">
              <Bell size={20} className="text-[#D4AF37]" />
            </div>
            <h2 className="text-lg font-heading font-bold text-white">预警设置</h2>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm text-gray-400">信号信心度阈值</label>
                <span className="text-sm font-mono text-white" data-testid="threshold-value">{alertThreshold}%</span>
              </div>
              <input
                type="range"
                min="50"
                max="100"
                step="5"
                value={alertThreshold}
                onChange={(e) => setAlertThreshold(parseInt(e.target.value))}
                data-testid="threshold-slider"
                className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-[#D4AF37]"
              />
              <p className="text-xs text-gray-500 mt-2">
                只有当信号信心度达到此阈值时才会发送通知。
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <button
            onClick={handleSave}
            disabled={saving}
            data-testid="save-button"
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-[#D4AF37] text-black font-bold rounded-sm hover:bg-[#B5952F] transition-colors disabled:opacity-50"
          >
            <Save size={18} />
            {saving ? '保存中...' : '保存设置'}
          </button>
        </motion.div>

        {/* 说明 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-6 glass-card rounded-sm p-6"
        >
          <h3 className="text-sm font-heading font-bold text-white mb-3">关于通知</h3>
          <p className="text-xs text-gray-400 leading-relaxed mb-2">
            系统会实时监控黄金价格和市场指标，当检测到明确的交易信号时，
            将通过邮件立即通知您。
          </p>
          <p className="text-xs text-gray-400 leading-relaxed">
            请确保您的邮箱地址正确，并将我们的邮件地址添加到白名单以确保接收。
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Settings;