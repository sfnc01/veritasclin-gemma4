from veritasclin.exporters.json_export import pack_to_json
from veritasclin.packs.builder import PackBuilder
from veritasclin.packs.loader import PackLoader


def test_pack_loader_loads_pack():
    pack, _ = PackBuilder().build("Dengue warning signs in adults", force_mock_retrieval=True)
    loaded = PackLoader().loads(pack_to_json(pack))
    assert loaded.pack_id == pack.pack_id
