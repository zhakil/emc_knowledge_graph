# services/integrations/kag_adapter.py
from kag.builder.component.reader.pdf_reader import PDFReader
from kag.builder.component.extractor.schema_constraint_extractor import SchemaConstraintExtractor
from kag.solver.main_solver import MainSolver
from kag.common.conf import KAG_CONFIG

class EMCKAGAdapter:
    """
    EMC项目的KAG适配器
    这个类封装了KAG的复杂性，提供了适合EMC场景的简单接口
    """
    
    def __init__(self, config_path=None):
        # 初始化KAG组件，但使用EMC项目的配置
        self.config = self._load_emc_kag_config(config_path)
        self.pdf_reader = PDFReader(self.config)
        self.extractor = SchemaConstraintExtractor(self.config)
        self.solver = MainSolver(self.config)
        
        # 加载EMC领域的特定配置
        self.emc_schema = self._load_emc_schema()
    
    def extract_from_emc_pdf(self, pdf_path):
        """
        从EMC PDF文档中提取知识
        这个方法将KAG的通用PDF处理能力适配为EMC特定的处理流程
        """
        # 使用KAG读取PDF
        content = self.pdf_reader.read(pdf_path)
        
        # 使用EMC特定的模式进行知识提取
        extracted_knowledge = self.extractor.extract(
            content, 
            schema=self.emc_schema,
            domain_context="EMC"  # 提供EMC领域上下文
        )
        
        # 转换为EMC项目期望的格式
        return self._convert_to_emc_format(extracted_knowledge)
    
    def _load_emc_kag_config(self, config_path):
        """
        加载适合EMC项目的KAG配置
        这里我们可以使用EMC项目现有的配置系统
        """
        emc_kag_config = {
            "llm": {
                "openai_client": {
                    "api_key": os.getenv("EMC_DEEPSEEK_API_KEY"),
                    "base_url": "https://api.deepseek.com/v1",
                    "model": "deepseek-chat"
                }
            },
            "neo4j": {
                "uri": os.getenv("NEO4J_URI"),
                "user": os.getenv("NEO4J_USERNAME"),
                "password": os.getenv("NEO4J_PASSWORD")
            }
        }
        return KAG_CONFIG.from_dict(emc_kag_config)