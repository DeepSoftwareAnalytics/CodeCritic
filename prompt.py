from openai import OpenAI
import json
import jsonlines
from datetime import datetime
import copy
import os

# os.environ["http_proxy"] = "http://localhost:7897"
# os.environ["https_proxy"] = "http://localhost:7897"

# api keys
with open('api_keys.txt', 'r', encoding='utf-8') as file:
    keys_list = file.read().splitlines()

client = OpenAI(
    api_key=keys_list[0]
)

# system_content
role = ("You are an expert code analyzer and will be provided with a piece of code for an algorithm question. "
        "Please analyze the code according to the following evaluation criteria to evaluate the code quality. I "
        "will also furnish you with three examples.\n")

criteria = ("(1)Is there any compilation error in the code? (2)Is the code functionally correct? (3)Is there an "
            "algorithm that is more efficient than the one used by the code? (4)Is the code too long or not "
            "concise enough? (5)Can the code judgment structure be simplified? (6)What is the cyclomatic "
            "complexity of the code? Is it too high? (7)What is the cognitive complexity of the code? Is it too "
            "high? (8)Are there any bad smells in the code? If so, please point them out.")

system_content = role + f"<Criteria>{criteria}</Criteria>\n"

# prompt_init
prompt_init = [{"role": "system", "content": system_content}]

# example
example_num = 3
for i in range(1, example_num + 1):
    with open(f'example/{i}/code.py', 'r', encoding='utf-8') as file:
        code = file.read()
    with open(f'example/{i}/feedback.txt', 'r', encoding='utf-8') as file:
        feedback = file.read()

    prompt_init.append({"role": "user", "content": f"<Code>{code}</Code>"})
    prompt_init.append({"role": "assistant", "content": feedback})


def get_response(messages):
    response = client.chat.completions.create(model="gpt-4", messages=messages)  # gpt-3.5-turbo
    return response.choices[0].message.content


def get_first_prompt(question, code):
    prompt = copy.deepcopy(prompt_init)  # 深拷贝

    user_content = (f"<Question>{question}</Question>\n" +
                    f"<Code>{code}</Code>\n")
    prompt.append({"role": "user", "content": user_content})

    # with open(f"prompt.json", "w", encoding='utf-8') as file:
    #     json.dump(prompt, file, indent=4)

    return prompt


def main():
    dataset = "test"
    num = 5200  # 从这开始
    with jsonlines.open(f'dataset/APPS_{dataset}.jsonl', 'r') as reader:
        for id, line in enumerate(reader):
            if id < num:  # 中断继续
                continue

            # 生成第一次prompt
            messages = get_first_prompt(line['question'], line['solution_code'])

            # 获取回复
            response = get_response(messages)
            # print(response)
            messages.append({"role": "assistant", "content": response})  # 维护对话历史

            # 保存数据
            data = {
                "id": id,
                "contestId": line["contestId"],
                "index": line["index"],
                "question": line["question"],
                "code": line["solution_code"],
                "feedback": response
            }
            with jsonlines.open(f"raw_data/data_{dataset}_raw.jsonl", mode='a') as writer:
                writer.write(data)

            # 保存对话历史
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            with open(f"chat_history/{dataset}/{id}_{current_time}.json", "w") as file:
                json.dump(messages, file, indent=4)
                print(f"序号 {id} 对话完成！")


if __name__ == "__main__":
    main()
