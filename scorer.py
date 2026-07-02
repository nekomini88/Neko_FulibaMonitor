def compute_score(item: dict) -> int:
    """
    Compute a score for the item based on title keywords and length.
    Returns an integer between 0 and 100.
    """
    title = item.get("title", "").lower()
    score = 50  # base score

    # Positive keywords (add points)
    positive_keywords = ['福利', '资源', '下载', '免费', '合集', '福利吧', '精品', '稀有', '福利', '漫画', '游戏', '软件']
    for kw in positive_keywords:
        if kw in title:
            score += 10
            if score > 100:
                score = 100

    # Negative keywords (subtract points)
    negative_keywords = ['广告', '公告', '失效', '过期', '删帖', '求助', '问答']
    for kw in negative_keywords:
        if kw in title:
            score -= 10
            if score < 0:
                score = 0

    # Length adjustment
    length = len(title)
    if length > 50:
        score += 10
        if score > 100:
            score = 100
    elif length > 30:
        score += 5
        if score > 100:
            score = 100

    if length < 10:
        score -= 10
        if score < 0:
            score = 0

    return score


def build_summary(item: dict, score: int) -> str:
    """
    Build a short summary string for the notification.
    """
    title = item.get("title", "无标题")
    link = item.get("link", "#")
    # We don't have a description, so just show title and score.
    # We can try to fetch a snippet from the page? For simplicity, we'll just show title.
    # Optionally, we can add the score and a link.
    return f"标题：{title}\n评分：{score}/100\n链接：{link}"