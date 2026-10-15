import pytest

from app.infrastructure.persistence import seed_products


@pytest.fixture(autouse=True, scope="session")
def _synthetic_sample_catalog():
    """单元测试围绕原合成样例编写（P1001 等编号与固定报价），显式使用样例目录。

    应用默认目录是 ESCI v2 真实商品；需要默认目录本身的测试直接读取对应常量。
    """
    default = seed_products._CATALOG_FIXTURE
    seed_products._CATALOG_FIXTURE = seed_products._PROJECT_ROOT / "data" / "catalog-demo.jsonl.gz"
    yield
    seed_products._CATALOG_FIXTURE = default
