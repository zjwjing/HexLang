"""
Hex64 训练数据扩充脚本

从现有 hexagrams.json 和 feedback.json 出发，通过多场景模板生成
大规模训练数据，目标达到 5000+ 条。

使用方式：
    python src/training/expand_data.py
    
输出：
    data/train_hex64_expanded.jsonl - 扩充后的训练数据
"""

import json
import sys
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

# Windows UTF-8 兼容
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class DataExpander:
    """训练数据扩充器"""
    
    # 多场景用户输入模板（统一使用{keyword}占位符）
    SCENARIOS = {
        "ops": [
            "{keyword} 错误",
            "系统出现 {keyword} 告警",
            "服务检测到 {keyword}",
            "监控发现 {keyword} 异常",
            "运维收到 {keyword} 通知",
            "{keyword} 导致服务降级",
            "生产环境 {keyword} 频发",
            "{keyword} 影响用户访问",
        ],
        "devops": [
            "部署时遇到 {keyword}",
            "CI/CD 流水线 {keyword}",
            "容器 {keyword} 退出",
            "Kubernetes {keyword} 事件",
            "自动化测试 {keyword}",
            "发布流程 {keyword}",
            "基础设施 {keyword}",
        ],
        "frontend": [
            "页面加载 {keyword}",
            "浏览器渲染 {keyword}",
            "前端组件 {keyword}",
            "CSS 布局 {keyword}",
            "JavaScript {keyword}",
            "移动端 {keyword}",
            "跨域请求 {keyword}",
        ],
        "backend": [
            "API 接口 {keyword}",
            "数据库查询 {keyword}",
            "微服务 {keyword}",
            "消息队列 {keyword}",
            "缓存层 {keyword}",
            "负载均衡 {keyword}",
            "后端服务 {keyword}",
        ],
        "security": [
            "安全扫描发现 {keyword}",
            "防火墙拦截 {keyword}",
            "SSL 证书 {keyword}",
            "认证失败 {keyword}",
            "权限校验 {keyword}",
            "漏洞检测 {keyword}",
            "DDoS 攻击 {keyword}",
        ],
        "data": [
            "ETL 管道 {keyword}",
            "数据仓库 {keyword}",
            "实时流 {keyword}",
            "数据一致性 {keyword}",
            "数据迁移 {keyword}",
            "数据质量 {keyword}",
            "索引优化 {keyword}",
        ],
        "performance": [
            "CPU 使用率 {keyword}",
            "内存泄漏 {keyword}",
            "磁盘 IO {keyword}",
            "网络延迟 {keyword}",
            "线程池 {keyword}",
            "GC 停顿 {keyword}",
            "连接池耗尽 {keyword}",
        ],
        "architecture": [
            "系统设计 {keyword}",
            "微服务拆分 {keyword}",
            "DDD 领域模型 {keyword}",
            "事件驱动 {keyword}",
            "CQRS 架构 {keyword}",
            "服务网格 {keyword}",
            "Serverless {keyword}",
        ],
        "testing": [
            "单元测试 {keyword}",
            "集成测试 {keyword}",
            "压力测试 {keyword}",
            "回归测试 {keyword}",
            "自动化测试 {keyword}",
            "测试覆盖率 {keyword}",
            "Mock 数据 {keyword}",
        ],
        "monitoring": [
            "日志分析 {keyword}",
            "链路追踪 {keyword}",
            "指标采集 {keyword}",
            "告警规则 {keyword}",
            "看板配置 {keyword}",
            "SLA 监控 {keyword}",
            "健康检查 {keyword}",
        ],
    }
    
    # 关键词库（按场景分类）
    KEYWORDS = {
        "ops": ["timeout", "OOM", "disk full", "cpu spike", "memory leak", "crash", "deadlock", "hang", "stuck", "unresponsive", "service down", "process killed"],
        "devops": ["build fail", "deploy error", "image pull", "pod crash", "configmap miss", "secret expired", "helm rollback", "ingress 502", "pipeline blocked", "artifact missing"],
        "frontend": ["layout shift", "hydration mismatch", "bundle size", "lazy load", "cache bust", "cors error", "websocket drop", "render blocking", "state lost", "css conflict"],
        "backend": ["connection refused", "query timeout", "index missing", "replication lag", "circuit open", "rate limit", "payload too large", "schema mismatch", "thread blocked", "socket closed"],
        "security": ["auth fail", "token expired", "xss detected", "sql injection", "csrf token", "privilege escalation", "cert expired", "brute force", "ip blocked", "session hijack"],
        "data": ["pipeline fail", "schema drift", "duplicate record", "null value", "type mismatch", "partition skew", "backlog growing", "stream lag", "etl broken", "warehouse sync"],
        "performance": ["gc pause", "thread pool", "context switch", "cache miss", "swap usage", "io wait", "network drop", "latency spike", "cpu throttling", "memory fragmentation"],
        "architecture": ["bottleneck", "coupling high", "scalability", "fault tolerance", "consistency", "availability", "partitioning", "sharding", "microservice split", "domain boundary"],
        "testing": ["assertion fail", "mock error", "coverage low", "race condition", "flaky test", "timeout", "dependency issue", "setup failed", "teardown error", "parallel execution"],
        "monitoring": ["metric drop", "alert storm", "dashboard empty", "log gap", "trace broken", "slo breach", "health check fail", "collector down", "buffer overflow", "sampling rate"],
    }
    
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = str(Path(__file__).parent.parent.parent)
        
        self.base_dir = Path(base_dir)
        self.hex_db_file = self.base_dir / 'data' / 'hexagrams.json'
        self.feedback_file = self.base_dir / 'data' / 'feedback.json'
        self.output_file = self.base_dir / 'data' / 'train_hex64_expanded.jsonl'
        
        # 系统提示词
        self.system_prompt = """你是 HexLang Assistant，基于 Qwen3-8B + Hex64 符号引擎。
你必须严格遵守以下规则：
1. 收到用户输入后，先进行 Hex64 转码。
2. 回答必须包含两段：[回复] 和 [Hex64 溯源]。
3. [Hex64 溯源] 格式：卦名（二进制）+ 语义标签。
4. 严禁使用玄学术语，严禁预测未来，保持工程化语气。
5. 若涉及运维告警，需给出具体处置建议。"""
    
    def load_json(self, path: Path) -> List[Dict[str, Any]]:
        """安全加载 JSON"""
        if not path.exists():
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except (json.JSONDecodeError, IOError):
            return []
    
    def find_hexagram(self, name: str) -> Optional[Dict[str, Any]]:
        """查找卦象信息"""
        hex_db = self.load_json(self.hex_db_file)
        for hex_item in hex_db:
            if hex_item.get('name') == name:
                return hex_item
        return None
    
    def generate_scenario_samples(self) -> List[Dict[str, Any]]:
        """生成多场景样本（主要扩充来源）"""
        hex_db = self.load_json(self.hex_db_file)
        samples = []
        
        # 不同场景的回复前缀模板列表（增加多样性）
        response_prefixes = {
            "ops": [
                "检测到运维场景下的信号：'{0}'。",
                "运维告警触发：'{0}'。",
                "生产环境监控到 '{0}' 异常。",
                "服务出现 '{0}' 故障。",
            ],
            "devops": [
                "CI/CD 流程中遇到 '{0}'。",
                "部署管道报告 '{0}' 错误。",
                "容器编排层检测到 '{0}'。",
                "基础设施监控显示 '{0}'。",
            ],
            "frontend": [
                "前端页面出现 '{0}' 问题。",
                "浏览器控制台报 '{0}' 错误。",
                "用户反馈页面 '{0}' 异常。",
                "渲染管线检测到 '{0}'。",
            ],
            "backend": [
                "后端服务报告 '{0}'。",
                "API 网关拦截到 '{0}' 请求。",
                "数据库层出现 '{0}' 异常。",
                "微服务间通信发生 '{0}'。",
            ],
            "security": [
                "安全扫描发现 '{0}' 威胁。",
                "IDS 系统告警：'{0}'。",
                "防火墙记录到 '{0}' 事件。",
                "渗透测试检测到 '{0}'。",
            ],
            "data": [
                "数据管道报告 '{0}'。",
                "ETL 流程中断于 '{0}'。",
                "数据仓库同步异常：'{0}'。",
                "数据质量检查发现 '{0}'。",
            ],
            "performance": [
                "性能监控告警：'{0}'。",
                "资源利用率超过阈值：'{0}'。",
                "系统响应变慢，疑似 '{0}'。",
                "压测结果异常：'{0}'。",
            ],
            "architecture": [
                "架构评审发现 '{0}' 风险。",
                "设计模式分析显示 '{0}'。",
                "系统架构存在 '{0}' 问题。",
                "技术债务评估：'{0}'。",
            ],
            "testing": [
                "测试框架报告 '{0}'。",
                "自动化测试失败：'{0}'。",
                "覆盖率分析发现 '{0}'。",
                "集成测试环节出现 '{0}'。",
            ],
            "monitoring": [
                "监控面板显示 '{0}' 异常。",
                "日志分析发现 '{0}' 模式。",
                "链路追踪标记 '{0}'。",
                "告警系统触发：'{0}'。",
            ],
        }
        
        # 不同场景的处置建议模板列表（增加多样性）
        suggestions = {
            "ops": [
                "建议立即执行：1.确认影响范围 2.执行紧急处置 3.进行根因分析",
                "标准操作流程：1.隔离故障节点 2.回滚至上一版本 3.排查日志",
                "应急方案：1.切换备用服务 2.清理缓存 3.重启实例",
            ],
            "security": [
                "安全响应流程：1.隔离受影响系统 2.启动应急响应 3.修复安全漏洞",
                "处置建议：1.吊销可疑凭证 2.更新安全策略 3.审计访问日志",
                "紧急措施：1.阻断恶意 IP 2.重置密钥 3.漏洞扫描",
            ],
            "performance": [
                "性能优化步骤：1.定位瓶颈点 2.优化资源分配 3.实施限流降级",
                "调优建议：1.分析慢查询 2.调整连接池 3.启用 CDN",
                "扩容方案：1.水平扩展 2.垂直升级 3.缓存预热",
            ],
        }
        
        for hex_info in hex_db:
            name = hex_info['name']
            tags = hex_info.get('tags', [])
            bin_code = hex_info.get('bin', '')
            
            for scenario_name, templates in self.SCENARIOS.items():
                keywords = self.KEYWORDS.get(scenario_name, ['error'])
                
                for template in templates:
                    for keyword in keywords[:3]:
                        user_input = f"[{name}] {template.replace('{keyword}', keyword)}"
                        
                        # 选择随机前缀和建议（增加多样性）
                        prefixes = response_prefixes.get(scenario_name, 
                            [f"检测到{scenario_name}场景信号：'{0}'。"])
                        prefix = random.choice(prefixes).format(keyword)
                        
                        if scenario_name in suggestions:
                            suggestion_list = suggestions[scenario_name]
                            suggestion = random.choice(suggestion_list)
                        else:
                            sample_tags = tags[:3] if tags else ['error']
                            suggestion = f"建议按 {'、'.join(sample_tags)} 逻辑处置"
                        
                        assistant_response = (
                            f"[回复] {prefix}\n"
                            f"依据 Hex64 符号映射，判定为{name}卦象。\n"
                            f"{suggestion}\n"
                            f"[Hex64 溯源：{name}({bin_code})，"
                            f"语义标签：{', '.join(tags)}]"
                        )
                        
                        samples.append({
                            "messages": [
                                {"role": "system", "content": self.system_prompt},
                                {"role": "user", "content": user_input},
                                {"role": "assistant", "content": assistant_response}
                            ]
                        })
        
        return samples
    
    def generate_augmented_questions(self) -> List[Dict[str, Any]]:
        """生成增强型问题（基于标签的工程问题）"""
        hex_db = self.load_json(self.hex_db_file)
        samples = []
        
        # 修复后的问题模板 — category 和 tag 使用不同的字段
        question_templates = [
            ("系统设计", "闭塞"),       # (category_placeholder, tag_placeholder)
            ("故障排查", "阻塞"),
            ("性能优化", "停滞"),
            ("代码重构", "拒绝"),
            ("缓存策略", "阻断"),
            ("服务降级", "暂停"),
            ("容错机制", "恢复"),
            ("负载均衡", "分发"),
            ("消息队列", "缓冲"),
            ("幂等设计", "去重"),
        ]
        
        for hex_info in hex_db:
            name = hex_info['name']
            tags = hex_info.get('tags', [])
            bin_code = hex_info.get('bin', '')
            english = hex_info.get('english', '')
            
            # 使用预定义的问题模板（不依赖可能重复的 category/tag）
            for eng_name, example_tag in question_templates[:4]:
                user_input = f"{eng_name}中如何处理{name}（{english}）问题？"
                
                assistant_response = (
                    f"[回复] {name}（{english}）对应 Hex64 的核心语义是：{', '.join(tags)}。"
                    f"在{eng_name}场景中，建议结合卦象特征制定策略。\n"
                    f"[Hex64 溯源：{name}({bin_code})，"
                    f"语义标签：{', '.join(tags)}]"
                )
                
                samples.append({
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": assistant_response}
                    ]
                })
        
        return samples
    
    def generate_feedback_variations(self) -> List[Dict[str, Any]]:
        """基于 feedback.json 生成变体"""
        feedbacks = self.load_json(self.feedback_file)
        samples = []
        
        for feedback in feedbacks:
            user_input = feedback.get('user_input', '')
            target_hex = feedback.get('target_hex', '')
            scene = feedback.get('scene', 'ops')
            
            if not user_input or not target_hex:
                continue
            
            hex_info = self.find_hexagram(target_hex)
            if not hex_info:
                continue
            
            tags = hex_info.get('tags', [])
            bin_code = hex_info.get('bin', '')
            english = hex_info.get('english', '')
            
            # 生成多种问法
            variations = [
                f"{user_input}",
                f"系统出现{user_input}错误",
                f"告警：{user_input}",
                f"监控发现{user_input}异常",
                f"如何处理{user_input}？",
            ]
            
            for var in variations:
                assistant_response = (
                    f"[回复] 检测到{scene}场景下的信号。"
                    f"根据 Hex64 符号映射，判定为{target_hex}（{english}）卦象。\n"
                    f"建议执行相应处置逻辑。\n"
                    f"[Hex64 溯源：{target_hex}({bin_code})，"
                    f"语义标签：{', '.join(tags)}]"
                )
                
                samples.append({
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": var},
                        {"role": "assistant", "content": assistant_response}
                    ]
                })
        
        return samples
    
    def expand(self, target_count: int = 5000) -> int:
        """
        扩充训练数据
        
        Args:
            target_count: 目标数据量
            
        Returns:
            生成的数据条数
        """
        print("\n=== Hex64 训练数据扩充 ===")
        print(f"目标数据量: {target_count} 条\n")
        
        all_samples = []
        
        # 1. 多场景样本（主要来源）
        print("1. 生成多场景样本...")
        scenario_samples = self.generate_scenario_samples()
        all_samples.extend(scenario_samples)
        print(f"   生成 {len(scenario_samples)} 条")
        
        # 2. 增强型问题
        print("2. 生成增强型问题...")
        augmented_samples = self.generate_augmented_questions()
        all_samples.extend(augmented_samples)
        print(f"   生成 {len(augmented_samples)} 条")
        
        # 3. Feedback 变体
        print("3. 生成 Feedback 变体...")
        feedback_samples = self.generate_feedback_variations()
        all_samples.extend(feedback_samples)
        print(f"   生成 {len(feedback_samples)} 条")
        
        # 4. 去重（基于 user_input 完全匹配）
        print("4. 去重处理...")
        unique_samples = self._deduplicate(all_samples)
        print(f"   去重后: {len(unique_samples)} 条")
        
        # 5. 打乱
        random.shuffle(unique_samples)
        
        # 6. 保存
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for item in unique_samples:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"\n[OK] 数据扩充完成！")
        print(f"   总数据量: {len(unique_samples)} 条")
        print(f"   输出文件: {self.output_file}")
        
        # 7. 质量抽样检查
        print("\n--- 质量抽样 ---")
        for i in [0, len(unique_samples)//4, len(unique_samples)//2, 3*len(unique_samples)//4, -1]:
            sample = unique_samples[i]
            ui = sample['messages'][1]['content']
            ar = sample['messages'][2]['content']
            has_brace = '{' in ui and '}' in ui
            status = "❌" if has_brace else "✅"
            print(f"   {status} user_input: {ui[:60]}...")
            if has_brace:
                print(f"      ⚠️ 警告: 发现未替换的占位符!")
        
        return len(unique_samples)
    
    def _deduplicate(self, samples: List[Dict], threshold: float = 0.8) -> List[Dict]:
        """基于 user_input 相似度去重"""
        unique = []
        seen_inputs = set()
        
        for sample in samples:
            user_input = sample['messages'][1]['content']
            
            # 简单哈希去重（完全相同）
            input_hash = hash(user_input)
            if input_hash not in seen_inputs:
                seen_inputs.add(input_hash)
                unique.append(sample)
        
        return unique


def main():
    """主函数"""
    expander = DataExpander()
    count = expander.expand(target_count=5000)
    
    if count >= 5000:
        print(f"\n[INFO] 数据扩充达标！下一步：")
        print(f"   1. 复制文件: cp {expander.output_file} data/train_hex64.jsonl")
        print(f"   2. 重新训练: python src/training/train_lora_native.py")
    else:
        print(f"\n[WARN] 数据量未达 5000 条，可考虑增加模板或关键词")


if __name__ == '__main__':
    main()
