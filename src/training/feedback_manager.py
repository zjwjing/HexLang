"""
HexLang - 符号编码系统

Copyright (c) 2026 zjwjing

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Hex64 Feedback 闭环管理系统

功能：
1. 自动收集用户反馈（正确/修正卦象）
2. 去重和置信度衰减
3. Adapter 版本管理 + 回滚
4. 自动重训触发（达到阈值时）

使用方式：
    # 收集反馈
    python src/training/feedback_manager.py --add "user_input" "target_hex" "ops"
    
    # 查看统计
    python src/training/feedback_manager.py --stats
    
    # 重新生成训练数据
    python src/training/feedback_manager.py --regenerate
    
    # 重新训练（如果反馈积累到阈值）
    python src/training/feedback_manager.py --train
    
    # 列出所有 adapter 版本
    python src/training/feedback_manager.py --versions
    
    # 回滚到指定版本
    python src/training/feedback_manager.py --rollback v0.1.0
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from shutil import copytree, rmtree

# Windows UTF-8 兼容
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class FeedbackManager:
    """Feedback 闭环管理器"""
    
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = str(Path(__file__).parent.parent.parent)
        
        self.base_dir = Path(base_dir)
        self.feedback_file = self.base_dir / 'data' / 'feedback.json'
        self.adapters_dir = self.base_dir / 'adapters'
        self.version_file = self.adapters_dir / 'versions.json'
        
        # 自动重训阈值
        self.train_threshold = 50  # 新增 50 条反馈触发重训
        self.decay_days = 30       # 30 天后置信度衰减 50%
        
        # 初始化版本记录
        self._init_versions()
    
    def _init_versions(self):
        """初始化版本记录文件"""
        if not self.version_file.exists():
            self.version_file.parent.mkdir(parents=True, exist_ok=True)
            versions = {
                "current": None,
                "history": []
            }
            self._save_json(self.version_file, versions)
    
    def _load_json(self, path: Path) -> Any:
        """安全加载 JSON"""
        if not path.exists():
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except (json.JSONDecodeError, IOError):
            return []
    
    def _save_json(self, path: Path, data: Any):
        """保存 JSON"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _make_feedback_key(self, user_input: str, target_hex: str) -> str:
        """生成反馈唯一键（去重用）"""
        raw = f"{user_input}|{target_hex}"
        return hashlib.md5(raw.encode('utf-8')).hexdigest()
    
    def add_feedback(
        self,
        user_input: str,
        target_hex: str,
        scene: str = "general",
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        添加单条反馈
        
        Args:
            user_input: 用户输入文本
            target_hex: 目标卦名（修正后的）
            scene: 场景标签（ops/devops/system 等）
            confidence: 置信度（0-1）
            
        Returns:
            反馈记录
        """
        feedbacks = self._load_json(self.feedback_file)
        
        # 去重检查
        key = self._make_feedback_key(user_input, target_hex)
        for fb in feedbacks:
            if fb.get('key') == key:
                # 更新置信度（取最高值）
                fb['confidence'] = max(fb.get('confidence', 0), confidence)
                fb['updated_at'] = datetime.now().isoformat()
                self._save_json(self.feedback_file, feedbacks)
                return fb
        
        # 新建反馈
        record = {
            "key": key,
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "original_hex": None,  # 可由 encoder 填充
            "target_hex": target_hex,
            "scene": scene,
            "confidence": confidence,
            "parsed": True,
            "updated_at": datetime.now().isoformat()
        }
        
        feedbacks.append(record)
        self._save_json(self.feedback_file, feedbacks)
        
        print(f"✅ 添加反馈: {user_input[:30]}... → {target_hex}")
        
        # 检查是否达到重训阈值
        new_count = sum(1 for fb in feedbacks if fb.get('parsed'))
        if new_count >= self.train_threshold:
            print(f"\n⚡ 反馈数量达到阈值 ({new_count}/{self.train_threshold})，建议运行 --train")
        
        return record
    
    def get_stats(self) -> Dict[str, Any]:
        """获取反馈统计信息"""
        feedbacks = self._load_json(self.feedback_file)
        
        total = len(feedbacks)
        parsed = sum(1 for fb in feedbacks if fb.get('parsed'))
        scenes = {}
        hexes = {}
        
        for fb in feedbacks:
            scene = fb.get('scene', 'unknown')
            scenes[scene] = scenes.get(scene, 0) + 1
            
            hex_name = fb.get('target_hex', 'unknown')
            hexes[hex_name] = hexes.get(hex_name, 0) + 1
        
        # 按置信度分组
        high_conf = sum(1 for fb in feedbacks if fb.get('confidence', 0) >= 0.8)
        mid_conf = sum(1 for fb in feedbacks if 0.5 <= fb.get('confidence', 0) < 0.8)
        low_conf = sum(1 for fb in feedbacks if fb.get('confidence', 0) < 0.5)
        
        stats = {
            "total": total,
            "parsed": parsed,
            "scenes": dict(sorted(scenes.items(), key=lambda x: -x[1])),
            "top_hexes": dict(sorted(hexes.items(), key=lambda x: -x[1])[:10]),
            "confidence_distribution": {
                "high(>=0.8)": high_conf,
                "mid(0.5-0.8)": mid_conf,
                "low(<0.5)": low_conf
            },
            "ready_for_training": parsed >= self.train_threshold
        }
        
        return stats
    
    def apply_confidence_decay(self):
        """应用置信度衰减（超过 decay_days 的反馈降低权重）"""
        feedbacks = self._load_json(self.feedback_file)
        now = datetime.now()
        decayed = 0
        
        for fb in feedbacks:
            updated = fb.get('updated_at')
            if not updated:
                continue
            
            try:
                last_update = datetime.fromisoformat(updated)
                days_ago = (now - last_update).days
                
                if days_ago > self.decay_days:
                    old_conf = fb.get('confidence', 1.0)
                    fb['confidence'] = old_conf * 0.5
                    fb['decayed'] = True
                    decayed += 1
            except (ValueError, TypeError):
                pass
        
        if decayed > 0:
            self._save_json(self.feedback_file, feedbacks)
            print(f"⏰ 置信度衰减完成: {decayed} 条反馈权重降低")
        else:
            print("✅ 无需衰减：所有反馈都在有效期内")
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """列出所有 adapter 版本"""
        if not self.version_file.exists():
            return []
        
        versions_data = self._load_json(self.version_file)
        return versions_data.get('history', [])
    
    def save_version(self, adapter_path: str, label: str = None) -> Dict[str, Any]:
        """
        保存当前 adapter 为版本
        
        Args:
            adapter_path: adapter 目录路径
            label: 版本标签（如 v1.0.0），自动生成如果未提供
            
        Returns:
            版本信息
        """
        if not os.path.exists(adapter_path):
            raise FileNotFoundError(f"Adapter 路径不存在: {adapter_path}")
        
        # 生成版本号
        versions = self.list_versions()
        if not versions:
            version_num = "v0.1.0"
        else:
            latest = versions[0]['version']
            parts = latest.split('.')
            parts[-1] = str(int(parts[-1]) + 1)
            version_num = '.'.join(parts)
        
        if label:
            version_num = label
        
        # 复制 adapter 到版本目录
        version_dir = self.adapters_dir / version_num
        if version_dir.exists():
            rmtree(version_dir)
        copytree(adapter_path, str(version_dir))
        
        # 记录版本信息
        version_info = {
            "version": version_num,
            "timestamp": datetime.now().isoformat(),
            "source": adapter_path,
            "size_mb": sum(
                os.path.getsize(os.path.join(dirpath, f))
                for dirpath, dirnames, filenames in os.walk(version_dir)
                for f in filenames
            ) / (1024 * 1024),
            "feedback_count": len(self._load_json(self.feedback_file)),
            "label": version_info.get('label', label)
        }
        
        versions_data = self._load_json(self.version_file)
        versions_data['current'] = version_num
        versions_data['history'].insert(0, version_info)
        self._save_json(self.version_file, versions_data)
        
        print(f"💾 保存版本: {version_num} ({version_info['size_mb']:.1f} MB)")
        
        return version_info
    
    def rollback(self, version: str) -> bool:
        """
        回滚到指定版本
        
        Args:
            version: 版本号（如 v0.1.0）
            
        Returns:
            是否成功
        """
        version_dir = self.adapters_dir / version
        
        if not version_dir.exists():
            print(f"❌ 版本不存在: {version}")
            return False
        
        # 恢复为当前 adapter
        current_dir = self.adapters_dir / 'hex64-v1'
        if current_dir.exists():
            rmtree(current_dir)
        copytree(str(version_dir), str(current_dir))
        
        # 更新版本记录
        versions_data = self._load_json(self.version_file)
        versions_data['current'] = version
        versions_data['history'].insert(0, {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "action": "rollback"
        })
        self._save_json(self.version_file, versions_data)
        
        print(f"↩️  已回滚到版本: {version}")
        return True
    
    def regenerate_training_data(self) -> int:
        """重新生成训练数据（从 feedback.json）"""
        sys.path.insert(0, str(Path(__file__).parent))
        from prepare_data import DataPreparer
        
        preparer = DataPreparer(str(self.base_dir))
        count = preparer.prepare()
        
        print(f"\n🔄 训练数据重新生成完成: {count} 条")
        return count
    
    def check_train_ready(self) -> bool:
        """检查是否达到重训条件"""
        stats = self.get_stats()
        return stats['ready_for_training']
    
    def trigger_retrain(self, max_steps: int = 300, lora_rank: int = 16) -> bool:
        """
        触发重新训练
        
        Args:
            max_steps: 训练步数
            lora_rank: LoRA 秩
            
        Returns:
            是否成功启动训练
        """
        if not self.check_train_ready():
            stats = self.get_stats()
            print(f"❌ 未达到重训阈值: {stats['parsed']}/{self.train_threshold}")
            return False
        
        print(f"\n⚡ 开始重新训练...")
        print(f"   反馈数据: {self.get_stats()['parsed']} 条")
        print(f"   训练步数: {max_steps}")
        print(f"   LoRA rank: {lora_rank}\n")
        
        # 1. 重新生成训练数据
        self.regenerate_training_data()
        
        # 2. 调用训练脚本
        train_script = self.base_dir / 'src' / 'training' / 'train_lora.py'
        
        import subprocess
        cmd = [
            sys.executable, str(train_script),
            '--steps', str(max_steps),
            '--rank', str(lora_rank),
            '--lr', '3e-4',
            '--batch-size', '2'
        ]
        
        print(f"执行命令: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, cwd=str(self.base_dir))
        
        if result.returncode == 0:
            print("\n✅ 训练完成！")
            # 3. 保存新版本
            self.save_version('adapters/hex64-v1')
            return True
        else:
            print("\n❌ 训练失败")
            return False


def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hex64 Feedback 闭环管理')
    parser.add_argument('--add', nargs=3, metavar=('INPUT', 'HEX', 'SCENE'),
                       help='添加反馈')
    parser.add_argument('--stats', action='store_true', help='显示统计')
    parser.add_argument('--decay', action='store_true', help='应用置信度衰减')
    parser.add_argument('--regenerate', action='store_true', help='重新生成训练数据')
    parser.add_argument('--train', action='store_true', help='触发重训')
    parser.add_argument('--versions', action='store_true', help='列出所有版本')
    parser.add_argument('--rollback', type=str, help='回滚到指定版本')
    parser.add_argument('--check', action='store_true', help='检查是否可重训')
    
    args = parser.parse_args()
    
    manager = FeedbackManager()
    
    if args.add:
        user_input, target_hex, scene = args.add
        manager.add_feedback(user_input, target_hex, scene)
    
    elif args.stats:
        stats = manager.get_stats()
        print("\n=== Feedback 统计 ===")
        print(f"总反馈数: {stats['total']}")
        print(f"有效反馈: {stats['parsed']}")
        print(f"可重训: {'是' if stats['ready_for_training'] else '否'}")
        print(f"\n场景分布:")
        for scene, count in stats['scenes'].items():
            print(f"  {scene}: {count}")
        print(f"\nTop 卦象:")
        for hex_name, count in stats['top_hexes'].items():
            print(f"  {hex_name}: {count}")
        print(f"\n置信度分布:")
        for level, count in stats['confidence_distribution'].items():
            print(f"  {level}: {count}")
    
    elif args.decay:
        manager.apply_confidence_decay()
    
    elif args.regenerate:
        manager.regenerate_training_data()
    
    elif args.train:
        manager.trigger_retrain()
    
    elif args.versions:
        versions = manager.list_versions()
        if not versions:
            print("无历史版本")
        else:
            print("\n=== Adapter 版本历史 ===")
            for v in versions[:5]:
                ts = v.get('timestamp', 'unknown')[:19]
                size = v.get('size_mb', 0)
                print(f"  {v['version']} ({ts}) - {size:.1f} MB")
    
    elif args.rollback:
        manager.rollback(args.rollback)
    
    elif args.check:
        ready = manager.check_train_ready()
        stats = manager.get_stats()
        print(f"\n重训状态: {'✅ 可以重训' if ready else '❌ 还需 ' + str(manager.train_threshold - stats['parsed']) + ' 条反馈'}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
