import unittest
from unittest.mock import Mock
from pipeline_indexador.src.pipeline.index_pipeline import IndexPipeline
from pipeline_indexador.src.stages.preprocess_stage import PreprocessStage
from pipeline_indexador.src.stages.tokenize_stage import TokenizeStage
from pipeline_indexador.src.stages.remove_stopwords_stage import RemoveStopwordsStage
from pipeline_indexador.src.stages.index_build_stage import IndexBuildStage


class TestIndexPipeline(unittest.TestCase):
    def setUp(self):
        self.mock_index_repository = Mock()

    def test_full_pipeline(self):
        pipeline = IndexPipeline(index_repository=self.mock_index_repository)
        # Ensure the pipeline has the expected stages in order
        self.assertIsInstance(pipeline.stages[0], PreprocessStage)
        self.assertIsInstance(pipeline.stages[1], TokenizeStage)
        self.assertIsInstance(pipeline.stages[2], RemoveStopwordsStage)
        self.assertIsInstance(pipeline.stages[3], IndexBuildStage)

        sample_text = "Este é um exemplo de texto para teste, com algumas palavras comuns e pontuação."
        expected_tokens_after_preprocessing = [
            "exemplo", "texto", "teste", "palavras", "comuns", "pontuacao"
        ]
        context = {"document_id": "doc1", "text": sample_text}
        
        result_context = pipeline.run(context)
        
        self.assertIn("tokens", result_context)
        self.assertIsInstance(result_context["tokens"], list)
        self.assertEqual(result_context["tokens"], expected_tokens_after_preprocessing)
        self.mock_index_repository.add_tokens.assert_called_once_with("doc1", expected_tokens_after_preprocessing)

    def test_pipeline_with_default_stopwords_expanded(self):
        pipeline = IndexPipeline(index_repository=self.mock_index_repository)

        sample_text = "Este é um exemplo de texto para teste."
        # 'este', 'e', 'um', 'de', 'para' are part of the expanded default stopwords
        # 'exemplo', 'teste' are not in the default stopwords
        expected_tokens = ["exemplo", "texto", "teste"] 
        context = {"document_id": "doc2", "text": sample_text}

        result_context = pipeline.run(context)
        
        self.assertIn("tokens", result_context)
        self.assertIsInstance(result_context["tokens"], list)
        self.assertEqual(result_context["tokens"], expected_tokens)
        self.mock_index_repository.add_tokens.assert_called_once_with("doc2", expected_tokens)


if __name__ == '__main__':
    unittest.main()
