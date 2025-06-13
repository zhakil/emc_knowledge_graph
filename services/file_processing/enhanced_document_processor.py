# services/file_processing/enhanced_document_processor.py
from services.integrations.kag_adapter import EMCKAGAdapter
from services.file_processing.document_processor import DocumentProcessor

class EnhancedEMCDocumentProcessor(DocumentProcessor):
    """
    增强的EMC文档处理器
    这个类扩展了你现有的文档处理器，添加了KAG的知识提取能力
    """
    
    def __init__(self):
        super().__init__()  # 初始化你现有的文档处理器
        self.kag_adapter = EMCKAGAdapter()  # 初始化KAG适配器
    
    def process_document(self, file_path, use_kag=True):
        """
        处理文档，可选择是否使用KAG增强
        这个方法展示了如何将KAG集成到现有的处理流程中
        """
        # 使用你现有的基础处理逻辑
        basic_result = super().process_document(file_path)
        
        if use_kag and file_path.endswith('.pdf'):
            # 使用KAG进行增强处理
            try:
                kag_result = self.kag_adapter.extract_from_emc_pdf(file_path)
                # 将KAG的结果合并到基础结果中
                enhanced_result = self._merge_results(basic_result, kag_result)
                return enhanced_result
            except Exception as e:
                # 如果KAG处理失败，降级到基础处理
                logger.warning(f"KAG处理失败，使用基础处理: {e}")
                return basic_result
        
        return basic_result