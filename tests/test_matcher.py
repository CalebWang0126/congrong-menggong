from src.monitor.matcher import MsgMatcher


class TestMsgMatcher:
    def test_match_by_nickname_exact(self):
        matcher = MsgMatcher([{"nickname": "宝贝老婆", "remark": ""}])
        result = matcher.match("宝贝老婆")
        assert result == {"nickname": "宝贝老婆", "remark": ""}

    def test_match_by_remark(self):
        matcher = MsgMatcher([{"nickname": "小美", "remark": "老婆"}])
        result = matcher.match("老婆")
        assert result == {"nickname": "小美", "remark": "老婆"}

    def test_match_ignores_whitespace(self):
        matcher = MsgMatcher([{"nickname": "宝贝", "remark": ""}])
        result = matcher.match("  宝贝  ")
        assert result == {"nickname": "宝贝", "remark": ""}

    def test_no_match_returns_none(self):
        matcher = MsgMatcher([{"nickname": "宝贝老婆", "remark": ""}])
        result = matcher.match("同事小王")
        assert result is None

    def test_empty_targets_never_match(self):
        matcher = MsgMatcher([])
        assert matcher.match("任何人") is None

    def test_match_multiple_targets(self):
        matcher = MsgMatcher([
            {"nickname": "宝贝", "remark": ""},
            {"nickname": "妈妈", "remark": ""},
        ])
        assert matcher.match("妈妈") == {"nickname": "妈妈", "remark": ""}
        assert matcher.match("宝贝") == {"nickname": "宝贝", "remark": ""}

    def test_update_targets_replaces_list(self):
        matcher = MsgMatcher([{"nickname": "旧目标", "remark": ""}])
        matcher.update_targets([{"nickname": "新目标", "remark": ""}])
        assert matcher.match("旧目标") is None
        assert matcher.match("新目标") == {"nickname": "新目标", "remark": ""}

    def test_remark_takes_priority_over_nickname(self):
        """If sender matches remark, it's found even if nickname field differs."""
        matcher = MsgMatcher([{"nickname": "张三", "remark": "老婆"}])
        result = matcher.match("老婆")
        assert result is not None
        assert result["nickname"] == "张三"
