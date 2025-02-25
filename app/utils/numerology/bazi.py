from pydantic import BaseModel, Field
from typing import List, Dict, Any
import json
from app.utils.llm_helper import create_llm_client
from langchain_core.output_parsers import JsonOutputParser
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 新增命理分析模型
class BaziAnalysis(BaseModel):
    """八字命理分析模型"""
    basic_data_verification: str = Field(description="基础数据核验结果")
    four_pillars: str = Field(description="四柱排盘结果")
    pattern_determination: str = Field(description="格局判定结果")
    adjustment_system: str = Field(description="调候体系结果")
    ten_gods_analysis: str = Field(description="十神能量场分析结果")
    life_field_prediction: str = Field(description="人生领域预测结果")
    time_space_planning: str = Field(description="时空运势规划结果")
    customized_advice: str = Field(description="定制化建议体系")

class BirthInfo(BaseModel):
    """出生信息模型"""

    birth_time: str = Field(description="北京时间出生时间")
    birth_place: str = Field(description="出生地")

class FourPillars(BaseModel):
    """四柱排盘模型"""
    year_pillar: str = Field(description="年柱")
    month_pillar: str = Field(description="月柱")
    day_pillar: str = Field(description="日柱")
    hour_pillar: str = Field(description="时柱")
    five_elements: List[str] = Field(description="五行属性")

class FateAnalysis(BaseModel):
    """命理分析模型"""
    birth_info: BirthInfo
    four_pillars: FourPillars
    pattern_name: str = Field(description="格局名称")
    pattern_degree: float = Field(description="成格度百分比")
    risk_points: List[str] = Field(description="破格风险点")
    adjustment_gods: List[str] = Field(description="必要调候用神及其状态")
    ten_gods_analysis: str = Field(description="十神能量场分析")
    important_deities: List[str] = Field(description="重要神煞及其现实映射")
    career_development: str = Field(description="事业发展模型")
    wealth_structure: str = Field(description="财富结构分析")
    marriage_children: str = Field(description="婚姻子女推演")
    recent_guidance: str = Field(description="近期流年指引")
    long_term_planning: str = Field(description="中长期规划")
    customized_advice: str = Field(description="定制化建议体系")

class BaziPlannerChain:  
    def __init__(self):
        self.llm = create_llm_client("deepseek")
        
        
    def analyze_bazi(self, birth_info: Dict) -> BaziAnalysis:
        """根据生辰信息进行命理分析"""
        try:
            input_message = f"""你是一名专业的命理学大师，请根据以下结构对提供的生辰信息进行专业命理分析：
一、基础数据核验

出生时间校正

输入参数：
出生时间：{birth_info["birth_time"]}
出生地：{birth_info["birth_place"]}

要求：进行真太阳时换算，注明时差计算过程及时辰归属

二、核心框架分析

四柱排盘

输出格式：
年柱　月柱　日柱　时柱
天干地支　天干地支　天干地支　天干地支
（五行属性）　（五行属性）　（五行属性）　（五行属性）

格局判定

分析方法：《子平真诠》取格法

要求：注明格局名称、成格度百分比、破格风险点

调候体系

分析方法：《穷通宝鉴》月令调候

要求：列出必要调候用神及其存在状态

三、深度命理推演

十神能量场分析

包含：通根透干关系、生克制化路线图

重点：日主强弱、关键十神作用路径

神煞系统整合

要求：标注重要神煞并说明其现实映射

四、人生领域预测

事业发展模型

包含：《滴天髓》气势法领域适配

输出：十年大运关键节点、岗位适配禁忌

财富结构分析

要求：构建三维模型（量级/来源/周期）

注明财库状态及风险年份

婚姻子女推演

包含：正缘匹配算法、生育窗口期

输出：婚恋危机预警年份

五、时空运势规划

近期流年指引

要求：未来1年逐月吉凶事件提示

包含：节气转换关键点

中长期规划

输出：未来3-5年重大机遇/挑战时间表

标注重要转折年份

六、定制化建议体系

五行调理方案

包含：方位学调整、饮食建议

输出：关键物件的风水布局

决策优化指南

包含：年度最佳启动时段、贵人属相

注明需要规避的合作生肖

附加要求：

保持古典命理术语与现代心理学表述的平衡

关键结论需标注引用典籍（如《神峰通考》病药说）

重要年份预测需提供具体化解方案

对矛盾命理现象进行辩证分析


示例：
输入：
出生时间：2024-01-01 12:00:00
出生地：海淀区
输出：
年柱 月柱 日柱 时柱  
庚午 乙酉 己亥 癸酉  
（金火）（木金）（土水）（水金）  
八字基本分析
日主与月令
己土生于酉月（仲秋金旺），月令藏干辛金当权，金气旺盛
土生金月，日主失令，需火生扶、水润局
十神定位与通根透干
日主己土：坐亥水（正财），无本气根，依赖年支午火（印星）生扶
月干乙木（七杀）：坐酉金截脚，被年干庚金（伤官）合制 → 伤官合杀
时干癸水（偏财）：坐酉金（食神）生扶 → 食神生财
格局判定（《子平真诠》法）
假伤官格（月令酉金食神，但年透庚金伤官）
成格度：75%（伤官生财路线清晰，但七杀无制为隐患）
调候用神（《穷通宝鉴》法）
秋土需丙火暖局、癸水润泽 → 原局午火藏丁，癸水透干 → 调候得用
重要神煞
年支午火：禄神（被酉金穿害，主早年根基波动）
日支亥水：驿马（主奔波变动）
时柱癸酉：文昌（主技艺才华）
命理详细分析
个性特点
《神峰通考》病药说解析
病：七杀乙木坐酉金受克（执行力强但易冲动）
药：庚金伤官合杀（以智谋化解冲突）
具体表现：
工作中善用策略解决难题，但遇到不公时会激烈反抗（乙木七杀特性）
对财务敏锐，能发现他人忽略的商机（癸水偏财透干）
情绪易受环境影响，冬季易抑郁（亥水寒湿克午火）
事业
发展路线（《滴天髓》气势法）
最佳领域：技术研发、金融投资、跨境贸易（金水相生 + 驿马动）
关键节点：
2026 丙午年（印星发力）：易获权威认证或升职
2030 庚戌年（伤官见官）：慎防合同纠纷，需提前法律规避
岗位特质
适合独立性强、绩效提成制的工作（偏财透干不喜固定薪资）
忌与属兔领导长期合作（卯酉冲引发月柱动荡）
财运
三维财富模型（《御定子平》量化法）
量级：百万级（癸水偏财得酉金双生）
得财方式：
正财（工资）占比 30% → 亥水被酉金生
偏财（投资）占比 70% → 癸水透干坐长生
财库周期：
2028 戊申年（申亥穿破财库）：需提前购置不动产锁定资金
婚姻
正缘特征（《星平会海》红鸾算法）
配偶属相：虎、羊、兔为忌（寅巳申三刑 / 未亥半合 / 卯酉冲）
最佳婚期：2025 乙巳年（巳火冲动妻宫亥水）
危机预警
2033 癸丑年（丑午穿害）：婆媳矛盾易引发分居，需注意农历五月
健康
五行偏枯警示
金旺木折（乙木七杀受克）：需防肝胆疾病（2027 丁未年为重点）
水多火熄（午火被亥水克）：注意心脑血管，尤其冬季亥子丑月
子女
子息宫分析
时柱癸酉（食神生偏财）：首胎为女儿概率 70%
最佳生育流年：2031 辛亥年（金水相生助子女宫）
当前年龄及运势
虚岁 36（2025 乙巳年）
大运己丑（2020-2030）：比肩帮身，合作运佳但竞争加剧
2025 年关键点：
农历四月（巳月）：驿马动，利跨区域发展
农历八月（酉月）：三酉自刑，慎防投资失误
未来 1 年趋势与预测（2025 乙巳年）
事业：巳火印星冲亥水，有办公地点变动或团队重组
财运：农历十月（亥月）偏财旺，可把握短期投机机会
健康：巳亥冲引发头痛，需避免熬夜（尤其夜间 11-1 点）
流年预测
2025 乙巳年逐月指引
月份	节气	吉凶事件
正月	立春	丙火透干，利签约
四月	立夏	驿马星动，搬迁 / 出差
八月	白露	酉金伏吟，忌借贷
十一月	大雪	偏财入库，适购置固定资产
未来 3 到 5 年趋势与预测
2026 丙午年
午火禄神到位，收入增长 30%，但午午自刑引发内部竞争
2027 丁未年
丁火枭神夺食，注意知识产权纠纷（尤其农历六月）
2028 戊申年
申亥穿害妻宫，夫妻需共同旅行化解气场冲克
一生的命运预测
大周期划分
35-45 岁：庚寅运（伤官见官），创业黄金期但需合规经营
55-65 岁：壬辰运（财星破印），资产重组关键期，宜退居二线
一生将会遇到的劫难
2044 甲子年（60 岁）：子午冲提纲领，需防心脏手术（提前布局南方暖色系住宅）
2037 丁巳年（53 岁）：三巳冲亥，交通意外风险（忌申酉月自驾）
一生将会遇到的福报
2049 己巳年（65 岁）：巳火印星合禄，子女成就卓越反哺家庭
2026 丙午年（36 岁）：天乙贵人显，获关键政策资源扶持
综合建议
五行调理
办公位：坐南朝北，桌面放置红色玛瑙（补火）
饮食：多食红枣、南瓜（土），早餐忌冷饮
重大决策时机
每年立夏后启动新项目（巳午月火旺助运）
签约择吉日：优先选寅日（合亥水妻宫）
关键人脉
贵人属相：马、狗（午戌合火局）
忌与属鸡者合伙（酉酉自刑损财）

            """

            # 使用 DeepSeek 模型生成命理分析
            result = self.llm.invoke(input_message)

            # 记录原始输出以便调试
            logger.info(f"命理分析原始输出: {result}")
            return result.content

        except Exception as e:
            logger.error(f"命理分析失败: {str(e)}")
            logger.error("详细错误信息: ", exc_info=True)
            return "分析失败"
            

def analyze_bazi(birth_info: BirthInfo) -> FateAnalysis:
    """
    根据提供的生辰信息进行专业命理分析。
    
    @param birth_info: BirthInfo 出生信息
    @return: FateAnalysis 命理分析结果
    """
    # 进行基础数据核验
    # 这里可以添加真太阳时换算的逻辑
    # ...

    # 四柱排盘
    four_pillars = FourPillars(
        year_pillar="庚午",
        month_pillar="乙酉",
        day_pillar="己亥",
        hour_pillar="癸酉",
        five_elements=["金火", "木金", "土水", "水金"]
    )

    # 格局判定
    pattern_name = "假伤官格"
    pattern_degree = 75.0
    risk_points = ["七杀无制为隐患"]

    # 调候体系
    adjustment_gods = ["丙火", "癸水"]

    # 深度命理推演
    ten_gods_analysis = "日主强弱、关键十神作用路径分析"
    important_deities = ["禄神", "驿马", "文昌"]

    # 人生领域预测
    career_development = "最佳领域：技术研发、金融投资"
    wealth_structure = "三维财富模型分析"
    marriage_children = "正缘匹配算法分析"

    # 时空运势规划
    recent_guidance = "未来1年逐月吉凶事件提示"
    long_term_planning = "未来3-5年重大机遇/挑战时间表"

    # 定制化建议体系
    customized_advice = "五行调理方案与决策优化指南"

    return FateAnalysis(
        birth_info=birth_info,
        four_pillars=four_pillars,
        pattern_name=pattern_name,
        pattern_degree=pattern_degree,
        risk_points=risk_points,
        adjustment_gods=adjustment_gods,
        ten_gods_analysis=ten_gods_analysis,
        important_deities=important_deities,
        career_development=career_development,
        wealth_structure=wealth_structure,
        marriage_children=marriage_children,
        recent_guidance=recent_guidance,
        long_term_planning=long_term_planning,
        customized_advice=customized_advice
    )


