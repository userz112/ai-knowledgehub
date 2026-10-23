from app.ai.embedding import encode_text


def main():
    text = "公司员工每年可以享受10天带薪年假。"

    vector = encode_text(text)

    print("文本：", text)
    print("向量维度：", len(vector))
    print("前 10 个向量值：", vector[:10])

    assert len(vector) == 512, "向量维度不符合预期"

    print("Embedding 测试通过！")


if __name__ == "__main__":
    main()
