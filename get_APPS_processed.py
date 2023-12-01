import json
import jsonlines


def main():
    with open("../APPS/problem_ids.txt", "r") as file:
        problem_ids = file.read().splitlines()

    path = "test" # train

    for problem_id in problem_ids:
        with open(f"../APPS/APPS/{path}/{problem_id}/metadata.json", "r", encoding="utf-8") as file:
            metadata = json.load(file)

        url = metadata["url"]
        if not url.startswith("https://codeforces.com"):
            continue

        url_split = url.split("/")
        contestId = url_split[-2]
        index = url_split[-1]

        with open(f"../APPS/APPS/{path}/{problem_id}/question.txt", "r", encoding="utf-8") as file:
            question = file.read()

        with open(f"../APPS/APPS/{path}/{problem_id}/input_output.json", "r") as file:
            examples = json.load(file)
            inputs = examples["inputs"]
            outputs = examples["outputs"]

        with open(f"../APPS/APPS/{path}/{problem_id}/solutions.json", "r") as file:
            solutions = json.load(file)

        for i, solution in enumerate(solutions):
            if i > 2:  # 以3截断
                break

            print(problem_id + f": {i + 1}")

            problem = {
                "APPS_id": problem_id,
                "contestId": int(contestId),
                "index": index,
                "question": question,
                "inputs": inputs,
                "outputs": outputs,
                "solution_code": solution
            }

            with jsonlines.open(f"dataset/APPS_{path}.jsonl", mode='a') as writer:
                writer.write(problem)


if __name__ == "__main__":
    main()
