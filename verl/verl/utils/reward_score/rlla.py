# SPDX-License-Identifier: CC-BY-NC-4.0

import re
import json
import os
import math
from collections import Counter

def match_score(list1, list2):
    """Compute a similarity score considering element frequency, ignoring order."""
    if list1 == list2:
        return 1.0
    
    if os.getenv("REFINEDREWARD", 0) == "1":
        # print("REFINEDREWARD is set to 1, so strict match is used")
        if list1 != list2:
            return 0.0
    
    if not list1 or not list2:
        return 0.0

    count1 = Counter(list1)  # Frequency count for list1
    count2 = Counter(list2)  # Frequency count for list2

    intersection = sum(min(count1[k], count2[k]) for k in count1.keys() & count2.keys())
    max_possible = len(list1) + len(list2) - intersection

    return intersection / max_possible if max_possible > 0 else 0.0
    

# base tag format
def base_tag_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, tag, **kwargs):
    if str(os.getenv("MAX1STEP30MAX3", 0)) == "1":
        print("MAX1STEP30MAX3 is set to 1, so max 1 -> 30 steps -> max 3")
        if step >= 30:
            max_possible_reward = max_possible_reward / 2
            min_possible_reward = min_possible_reward / 2
        else:
            max_possible_reward = max_possible_reward
            min_possible_reward = min_possible_reward
    
    # schedule reward
    if str(os.getenv("SCHEDULEREWARD", 0)) == "1":
        print("SCHEDULEREWARD is set to 1, so schedule reward is used")
        max_possible_reward = 2 - (2 - max_possible_reward) * step / 150
        min_possible_reward = -2 + (2 + min_possible_reward) * step / 150
        if max_possible_reward < 1.0:
            max_possible_reward = 1.0
        if min_possible_reward > -1.0:
            min_possible_reward = -1.0
    
    rewards = []
    responses = [completion[0]['content'] for completion in completions]
    
    # print("\n======= Answer ======= ")
    # print(answer[0])
    # print("\n======= Responses ======= ")
    # for idx, response in enumerate(responses):
    #     print(f"*** Response {idx+1}***\n{response}")

    for response, ans in zip(responses, answer):
        reward = min_possible_reward
        if tag == "tool_call":
            if "<response>" not in ans and "<tool_call>" in ans:
                pattern = r"^<plan>.*?</plan>\n<tool_call>.*?</tool_call>$" 
                if re.search(pattern, response, re.DOTALL) and response.count("<tool_call>") == 1 and response.count("</tool_call>") == 1:
                    reward = max_possible_reward
            elif "<response>" in ans and "<tool_call>" in ans:
                pattern = r"^<plan>.*?</plan>\n<tool_call>.*?</tool_call>\n<response>.*?</response>$"
                if re.search(pattern, response, re.DOTALL) and response.count("<tool_call>") == 1 and response.count("</tool_call>") == 1 and response.count("<response>") == 1 and response.count("</response>") == 1:
                    reward = max_possible_reward
            else:
                reward = 0.0
        
        if tag == "plan":
            if "<plan>" in ans:
                pattern = r"^<plan>.*?</plan>.*?"
                if re.search(pattern, response, re.DOTALL) and response.count("<plan>") == 1 and response.count("</plan>") == 1:
                    reward = max_possible_reward
            else:
                reward = 0.0
        
        if tag == "response":
            if "<response>" in ans and "<tool_call>" not in ans:
                pattern = r"^<plan>.*?</plan>\n<response>.*?</response>$"
                if re.search(pattern, response, re.DOTALL) and response.count("<response>") == 1 and response.count("</response>") == 1:
                    reward = max_possible_reward
            elif "<response>" in ans and "<tool_call>" in ans:
                pattern = r"^<plan>.*?</plan>\n<tool_call>\n.*?\n</tool_call>\n<response>.*?</response>$"
                if re.search(pattern, response, re.DOTALL) and response.count("<tool_call>") == 1 and response.count("</tool_call>") == 1 and response.count("<response>") == 1 and response.count("</response>") == 1:
                    reward = max_possible_reward
            else:
                reward = 0.0
        # pattern = fr"^<{tag}>.*?</{tag}>$"
        # if f"<{tag}>" in ans and f"/<{tag}>" in ans:
        #     if re.search(pattern, response, re.DOTALL) and response.count(f"<{tag}>") == 1 and response.count(f"</{tag}>") == 1:
        #         reward = max_possible_reward
        rewards.append(reward)
        
    # print("\n======= Reward for <format> =======")
    # print("Reward function for <format> is called ...")
    # print(rewards)
    return rewards


# base content format
def base_content_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, tag, **kwargs):
    if str(os.getenv("MAX1STEP30MAX3", 0)) == "1":
        print("MAX1STEP30MAX3 is set to 1, so max 1 -> 30 steps -> max 3")
        if step >= 30:
            max_possible_reward = max_possible_reward / 2
            min_possible_reward = min_possible_reward / 2
        else:
            max_possible_reward = max_possible_reward
            min_possible_reward = min_possible_reward
    
    # schedule reward
    if str(os.getenv("SCHEDULEREWARD", 0)) == "1":
        print("SCHEDULEREWARD is set to 1, so schedule reward is used")
        max_possible_reward = 2 - (2 - max_possible_reward) * step / 150
        min_possible_reward = -2 + (2 + min_possible_reward) * step / 150
        if max_possible_reward < 1.0:
            max_possible_reward = 1.0
        if min_possible_reward > -1.0:
            min_possible_reward = -1.0
    
    rewards = []
    responses = [completion[0]['content'] for completion in completions]
    
    # print("\n======= Answer ======= ")
    # print(answer[0])
    # print("\n======= Responses ======= ")
    # for idx, response in enumerate(responses):
    #     print(f"*** Response {idx+1}***\n{response}")

    for response, ans in zip(responses, answer):
        reward = min_possible_reward

        if tag == "plan":
            if "<plan>" in ans:
                pattern = r"^<plan>.*?</plan>.*?"
                if re.search(pattern, response, re.DOTALL) and response.count("<plan>") == 1 and response.count("</plan>") == 1:
                    ans_plan = ans.split("<plan>")[1].split("</plan>")[0]
                    resp_plan = response.split("<plan>")[1].split("</plan>")[0]
                    if ans_plan == resp_plan:
                        reward = max_possible_reward
                    else:
                        score = match_score(ans_plan, resp_plan)
                        reward = score * (max_possible_reward - min_possible_reward)
            else:
                reward = 0.0
        
        elif tag == "response":
            if "<response>" in ans and "<tool_call>" not in ans:
                pattern = r"^<plan>.*?</plan>\n<response>.*?</response>$"
                if re.search(pattern, response, re.DOTALL) and response.count("<response>") == 1 and response.count("</response>") == 1:
                    ans_resp = ans.split("<response>")[1].split("</response>")[0]
                    resp_resp = response.split("<response>")[1].split("</response>")[0]
                    if ans_resp == resp_resp:
                        reward = max_possible_reward
                    else:
                        score = match_score(ans_resp, resp_resp)
                        reward = score * (max_possible_reward - min_possible_reward)
            elif "<response>" in ans and "<tool_call>" in ans:
                pattern = r"^<plan>.*?</plan>\n<tool_call>\n.*?\n</tool_call>\n<response>.*?</response>$"
                if re.search(pattern, response, re.DOTALL) and response.count("<tool_call>") == 1 and response.count("</tool_call>") == 1 and response.count("<response>") == 1 and response.count("</response>") == 1:
                    ans_resp = ans.split("<response>")[1].split("</response>")[0]
                    resp_resp = response.split("<response>")[1].split("</response>")[0]
                    if ans_resp == resp_resp:
                        reward = max_possible_reward
                    else:
                        score = match_score(ans_resp, resp_resp)
                        reward = score * (max_possible_reward - min_possible_reward)
            else:
                reward = 0.0
        rewards.append(reward)
        
    # print("\n======= Reward for <format> =======")
    # print("Reward function for <format> is called ...")
    # print(rewards)
    return rewards

# custoimzed reward functions: format
def customize_format_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, **kwargs):
    if str(os.getenv("MAX1STEP30MAX3", 0)) == "1":
        # print("MAX1STEP30MAX3 is set to 1, so max 1 -> 30 steps -> max 3")
        if step >= 30:
            max_possible_reward = max_possible_reward / 2
            min_possible_reward = min_possible_reward / 2
        else:
            max_possible_reward = max_possible_reward
            min_possible_reward = min_possible_reward
    
    # schedule reward
    if str(os.getenv("SCHEDULEREWARD", 0)) == "1":
        # print("SCHEDULEREWARD is set to 1, so schedule reward is used")
        max_possible_reward = 2 - (2 - max_possible_reward) * step / 150
        min_possible_reward = -2 + (2 + min_possible_reward) * step / 150
        if max_possible_reward < 1.0:
            max_possible_reward = 1.0
        if min_possible_reward > -1.0:
            min_possible_reward = -1.0
    
    rewards = []
    responses = [completion[0]['content'] for completion in completions]
    
    # print("\n======= Answer ======= ")
    # print(answer[0])
    # print("\n======= Responses ======= ")
    # for idx, response in enumerate(responses):
        # print(f"*** Response {idx+1}***\n{response}")

    for response, ans in zip(responses, answer):
        reward = min_possible_reward
        if "<response>" in ans and "<tool_call>" not in ans:
            pattern = r"^<plan>.*?</plan>\n<response>.*?</response>$"
            if re.search(pattern, response, re.DOTALL) and response.count("<response>") == 1 and response.count("</response>") == 1:
                reward = max_possible_reward
        elif "<response>" not in ans and "<tool_call>" in ans:
            pattern = r"^<plan>.*?</plan>\n<tool_call>\n.*?\n</tool_call>$" 
            if re.search(pattern, response, re.DOTALL) and response.count("<tool_call>") == 1 and response.count("</tool_call>") == 1:
                reward = max_possible_reward
        elif "<response>" in ans and "<tool_call>" in ans:
            pattern = r"^<plan>.*?</plan>\n<tool_call>\n.*?\n</tool_call>\n<response>.*?</response>$"
            if re.search(pattern, response, re.DOTALL) and response.count("<tool_call>") == 1 and response.count("</tool_call>") == 1 and response.count("<response>") == 1 and response.count("</response>") == 1:
                reward = max_possible_reward
        else:
            pattern = r"^<plan>.*?</plan>$"
            if re.search(pattern, response, re.DOTALL):
                reward = max_possible_reward
        
        rewards.append(reward)
        
    # print("\n======= Reward for <format> =======")
    # print("Reward function for <format> is called ...")
    # print(rewards)
    return rewards


# customized reward functions: length
def customize_length_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, **kwargs):
    # schedule length
    if os.getenv("SCHEDULELENGTH", 0) == "1":
        # print("SCHEDULELENGTH is set to 1, so schedule max reward for length is used")
        max_reward_len = (640 - 384) * step / 105 + 384
    else:
        max_reward_len = 512
    
    """Reward function that gives higher scores to longer completions."""
    responses = [completion[0]['content'] for completion in completions]
    rewards = []
    
    for response, ans in zip(responses, answer):
        if "<plan>" not in response or "</plan>" not in response:
            rewards.append(min_possible_reward)
            continue
        plan_responses = response.split("<plan>")[-1].split("</plan>")[0].strip()
        reward = round(len(plan_responses.split()) / max_reward_len, 2)
        if reward > 1.0:
            reward = 1.0
        
        final_reward = reward * (max_possible_reward - min_possible_reward) + min_possible_reward
        rewards.append(final_reward)
    
    # print("\n======= Reward for <length> =======")
    # print("Reward function for <length> is called ...")
    # print(rewards)
    return rewards
    
def compute_tool_call_reward(gt_tools, pd_tools, max_possible_reward, min_possible_reward):
    if gt_tools == pd_tools:
        # print("Max possible score:", "Exact Match!")
        # print("Score:", max_possible_reward)
        return max_possible_reward
    
    if os.getenv("COARSEREWARD", 0) == "1":
        # print("COARSEREWARD is set to 1, so coarse reward is used")
        if gt_tools != pd_tools:
            return min_possible_reward

    gt_names = [tool["name"] for tool in gt_tools]
    pd_names = [tool["name"] for tool in pd_tools]
    score = match_score(list(gt_names), list(pd_names))
    
    local_max_possible = 1.0
    used_pd_indices = set()  # Keep track of matched pd_tools

    for gt_tool in gt_tools:
        gt_name = gt_tool["name"]
        gt_params = gt_tool["parameters"]
        
        if str(os.getenv("INTERMEDIATEREWARD", 0)) == "1":
            # print("INTERMEDIATEREWARD is set to 1, so local max possible is changed")
            local_max_possible += 1.0
        else:
            local_max_possible += 1.0 + len(gt_params)
        
        best_match = None
        best_match_score = 0.0
        best_match_index = -1

        # Find the best matching unused pd_tool
        for i, pd_tool in enumerate(pd_tools):
            if i in used_pd_indices or pd_tool["name"] != gt_name:
                continue
            
            if str(os.getenv("INTERMEDIATEREWARD", 0)) == "1":
                if gt_tool == pd_tool:
                    best_match = pd_tool
                    best_match_index = i
                    best_match_score = 1.0
                    break
                else:
                    continue
            
            pd_params = pd_tool["parameters"]
            param_score = match_score(list(gt_params.keys()), list(pd_params.keys()))
            
            # Calculate correctness score for parameter values
            correctness_score = sum(1.0 for k, v in gt_params.items() if k in pd_params and pd_params[k] == v)

            total_score = param_score + correctness_score
            
            if total_score > best_match_score:
                best_match_score = total_score
                best_match = pd_tool
                best_match_index = i

        if best_match:
            used_pd_indices.add(best_match_index)
            score += best_match_score

    # print()
    # print("Max possible score:", local_max_possible)
    # print("Score:", score)
    
    return (max_possible_reward - min_possible_reward) * score / local_max_possible + min_possible_reward


def compute_negative_score(pd_tools, negative_list, decay_rate=1):
    pd_names = [tool["name"] for tool in pd_tools]
    negative_dict = {}
    for neg in negative_list:
        negative_dict[neg['name']] = float(neg['relevance'])
    negative_score = 0.
    for name in pd_names:
        if name in negative_dict.keys():
            negative_score += (1-negative_dict[name]) * decay_rate
        else:
            negative_score += (1-0) * decay_rate
        # elif is_min_possible_reward:
        #     negative_score += (1-0) * decay_rate
    negative_score = -1 * negative_score / len(pd_names)
    return negative_score

# custoimzed reward functions: tool call correctness
def customize_correctness_reward_tool(completions, answer, step, max_possible_reward, min_possible_reward, **kwargs):
    if str(os.getenv("MAX1STEP30MAX3", 0)) == "1":
        # print("MAX1STEP30MAX3 is set to 1, so max 1 -> 30 steps -> max 3")
        if step < 30:
            max_possible_reward = max_possible_reward / 3
            min_possible_reward = min_possible_reward / 3
        else:
            max_possible_reward = max_possible_reward
            min_possible_reward = min_possible_reward
    
    if str(os.getenv("SCHEDULEREWARD", 0)) == "1":
        # print("SCHEDULEREWARD is set to 1, so schedule reward is used")
        max_possible_reward = (max_possible_reward - 2) * step / 150 + 2
        min_possible_reward = (min_possible_reward + 2) * step / 150 - 2
        if max_possible_reward > 3.0:
            max_possible_reward = 3.0
        if min_possible_reward < -3.0:
            min_possible_reward = -3.0

    responses = [completion[0]['content'] for completion in completions]
    rewards = []

    print("\n======= Answer ======= ")
    print(answer[0])
    print("\n======= Responses ======= ")
    for idx, response in enumerate(responses):
        print(f"*** Response {idx+1}***\n{response}")

    for response, ans in zip(responses, answer):
        reward = 0.0
        if "<tool_call>" not in ans:
            # if "<tool_call>" not in response and "</tool_call>" not in response:
            #     reward = max_possible_reward
            # else:
            #     reward = min_possible_reward
            rewards.append(reward)
            continue

        gt_tool_call = ans.split("<tool_call>")[1].split("</tool_call>")[0].strip()
        gt_tools = gt_tool_call.split("\n")
        gt_tools = [json.loads(tool) for tool in gt_tools] # each diction contains "name" and "parameter"
        
        try:
            # Change here as a constrint in training: if the format is not correct, directly give the lowest possible score
            assert "<tool_call>" in response
            assert "</tool_call>" in response
            pd_tools = response.split("<tool_call>")[1].split("</tool_call>")[0].strip().split("\n")
            pd_tools = [json.loads(tool) for tool in pd_tools]
            
            reward = compute_tool_call_reward(gt_tools, pd_tools, max_possible_reward, min_possible_reward) # top reward is 2
            
            if str(os.getenv("ENABLENEGATIVE", 0)) == "1":
                # relevance_avg = 0.454
                # relevance_avg = 0.526
                # relevance_avg = 0.706
                decay_rate = float(os.getenv("DECAYRATE", 0.5))
                relevance_avg = float(os.getenv("AVGRELEVANCE", 0.5))
                # print(f"ENABLENEGATIVE is set to 1, so negative score is used. decay_rate={decay_rate}, relevance_avg={relevance_avg}")
                # print(f"old reward: {reward}")
                # # print(type(pd_tools))
                # print(f"pd_tools: {pd_tools}")
                # print(f"gt_tools: {gt_tools}")
                # print(f"negative_list: {kwargs['negative_list']}")
                try:
                    if str(os.getenv("NEGATIVEMODE", 0)) == "1":
                        # print("NEGATIVEMODE is set to 1, so schedule negative reward is used")
                        if step <= 150:
                            decay_rate = 0.5 - 0.3 * (step / 150)
                        else:
                            decay_rate = 0.2
                        negative_score = compute_negative_score(pd_tools, kwargs['negative_list'], decay_rate)
                        reward = max(min(reward + negative_score, max_possible_reward), min_possible_reward)
                        # print(f"negative_score: {negative_score}")
                        # print(f"new reward: {reward}")
                    else:
                        # print("NEGATIVEMODE is set to 0, so normal negative reward is used")
                        negative_score = compute_negative_score(pd_tools, kwargs['negative_list'], decay_rate)
                        reward = max(min((reward + negative_score) + decay_rate * (1-relevance_avg), max_possible_reward), min_possible_reward)
                        # print(f"negative_score: {negative_score}")
                        # print(f"new reward: {reward}")
                    
                except:
                    reward = reward  * 1
        except:
            reward = min_possible_reward
        
        rewards.append(reward)
    
    # print("\n======= Reward for <tool call> =======")
    # print("Reward function for <tool call> correctness is called ...")
    # print(rewards)
    return rewards

def timed_reward_function_dynamic_k(cur_step, total_step, k_formula='log'):
    """
    考虑 total_step 动态地计算 k 值的指数衰减权重函数

    参数:
    - cur_step: 当前步骤，从 1 开始计数
    - total_step: 总步骤数
    - k_formula: 使用哪种公式来计算动态的 k（'sqrt', 'log'）

    返回:
    - 权重值 (weight)
    """
    # 参数校验
    if cur_step > total_step:
        raise ValueError("cur_step 必须在 0 和 total_step 之间")
    if total_step <= 0:
        # print(total_step)
        raise ValueError("total_step 必须是正整数")
    
    # 动态计算 k
    if k_formula == 'sqrt':
        k = math.sqrt(total_step)
    elif k_formula == 'log':
        k = math.log(total_step + 1)
    else:
        raise ValueError("k_formula 必须是 'sqrt' 或 'log'")
    
    # 动态衰减率计算
    decay_rate = k / total_step  # 根据 total_step 和动态 k 计算衰减率
    # 指数衰减公式
    weight = math.exp(-decay_rate * (cur_step - 1))
    # print("\n======= Reward for <tool call> =======")
    # print("Reward function for <tool call> temporary is called ...")
    # print(weight)
    return weight

# response format
def response_format_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, **kwargs):
    rewards = base_tag_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, "response")
    return rewards

# response format
def response_content_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, **kwargs):
    rewards = base_content_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, "response")
    return rewards

# tool_call format
def tool_call_format_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, **kwargs):
    rewards = base_tag_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, "tool_call")
    return rewards

# tool_call format
def tool_call_content_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, **kwargs):
    rewards = customize_correctness_reward_tool(completions, answer, step, max_possible_reward, min_possible_reward)
    return rewards

# global format
def global_format_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, **kwargs):
    rewards = base_tag_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, "plan")
    return rewards

# global format
def global_content_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, **kwargs):
    rewards = base_content_reward_func(completions, answer, step, max_possible_reward, min_possible_reward, "plan")
    return rewards

def compute_score(solution_str, ground_truth, extra_info, step=0):
    """The scoring function for GSM8k.

    Reference: Trung, Luong, et al. "Reft: Reasoning with reinforced fine-tuning." Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). 2024.

    Args:
        solution_str: the solution text
        ground_truth: the ground truth
        method: the method to extract the solution, choices are 'strict' and 'flexible'
        format_score: the score for the format
        score: the score for the correct answer
    """
    exp_name = str(os.getenv("EXPERIMENT_NAME", ""))
    if "llama" in exp_name:
        predict_str = solution_str.split("<|start_header_id|>assistant<|end_header_id|>")[-1].split("<|eot_id|>")[0].strip()
    elif "qwen" in exp_name:
        predict_str = solution_str.split("<|im_start|>assistant")[-1].split("<|im_end|>")[0].strip()
    else:
        raise NotImplementedError(f"Unknown model name: {exp_name}")
    
    if str(os.getenv("CORRECTMAX1", 0)) == "1":
        # print("CORRECTMAX1 is set to 1, so max score is set to 1")
        tool_max_possible = 1.0
        tool_min_possible = -1.0
    else:
        tool_max_possible = 3.0
        tool_min_possible = -3.0
    
    format_max_possible = 1.0
    format_min_possible = 0.0
    
    length_max_possible = 1.0
    length_min_possible = 0.0
    
    completions = [[{"role": "assistant", "content": predict_str}]]
    answer = [ground_truth]

    currentToolCount = extra_info['currentToolCount']
    totalToolCount = extra_info['totalToolCount']
    negative_list = json.loads(extra_info['negative'])
    tool_weight = float(os.getenv("TOOLWEIGHT", 0.2))
    global_weight = float(os.getenv("GLOBALWEIGHT", 0.1))

    print(f"tool_weight: {tool_weight}, effective coefficient: {tool_weight * 10}")
    print(f"global_weight: {global_weight}, effective coefficient: {global_weight * 10}")
    
    if str(os.getenv("TIMEWEIGHTFUNC", 0)) == "1":
        # print("TIMEWEIGHTFUNC is set to 1, so temporal reward is linear(1/z)")
        time_weight = 2 / (currentToolCount + 1)
    elif str(os.getenv("TIMEWEIGHTFUNC", 0)) == "2":
        # print("TIMEWEIGHTFUNC is set to 2, so temporal reward is discrete(0, 1, 2, 3...)")
        if currentToolCount <= 0:
            time_weight = 2.0
        elif currentToolCount <= 1:
            time_weight = 1.5
        elif currentToolCount <= 2:
            time_weight = 1.0
        elif currentToolCount <= 3:
            time_weight = 0.5 
        elif currentToolCount <= 4:
            time_weight = 0.4 
        elif currentToolCount <= 5:
            time_weight = 0.3 
        else:
            time_weight = 0.2
    else:
        # print("TIMEWEIGHTFUNC is set to 0, so temporal reward is exponential")
        if str(os.getenv("TIMEWEIGHTKFORMULA", 0)) == "1":
            # print("TIMEWEIGHTKFORMULA is set to 1, so k_formula = sqrt!")
            time_weight = timed_reward_function_dynamic_k(currentToolCount, totalToolCount, k_formula='sqrt')
        else:
            # print("TIMEWEIGHTKFORMULA is set to 0, so k_formula = log!")
            time_weight = timed_reward_function_dynamic_k(currentToolCount, totalToolCount, k_formula='log')

    response_format_score = response_format_reward_func(completions, answer, step, format_max_possible, format_min_possible)[0]
    response_content_score = response_content_reward_func(completions, answer, step, tool_max_possible, tool_min_possible)[0]
    global_format_score = global_format_reward_func(completions, answer, step, format_max_possible, format_min_possible)[0]
    global_content_score = global_content_reward_func(completions, answer, step, format_max_possible, format_min_possible)[0]
    tool_call_format_score = tool_call_format_reward_func(completions, answer, step, format_max_possible, format_min_possible)[0]
    tool_call_content_score = customize_correctness_reward_tool(completions, answer, step, tool_max_possible, tool_min_possible, negative_list=negative_list)[0]

    print(f"response_format_score: {response_format_score}, response_content_score: {response_content_score}")
    print(f"plan_format_score: {global_format_score}, [plan_content_score: {global_content_score}")
    print(f"tool_call_format_score: {tool_call_format_score}, tool_call_content_score: {tool_call_content_score}")

    fomrat_score = (tool_weight * 10) * tool_call_format_score + (global_weight * 10) * global_format_score
    correctness_score = (tool_weight * 10) * tool_call_content_score + (global_weight * 10) * global_content_score
    
    if str(os.getenv("WITHLENGTH", 0)) == "1":
        # print("WITHLENGTH is set to 1, so length score is set!")
        length_score = customize_length_reward_func(completions, answer, step, length_max_possible, length_min_possible)[0]
    else:
        length_score = 0
    
    if str(os.getenv("TIMEWEIGHTMODE", 0)) == "1":
        # print("TIMEWEIGHTMODE is set to 1, so time_weight is applied for correctness_score!")
        score = fomrat_score + time_weight * correctness_score + length_score
    if str(os.getenv("TIMEWEIGHTMODE", 0)) == "2":
        # print("TIMEWEIGHTMODE is set to 2, so time_weight is applied for correctness_score and fomrat_score!")
        score = time_weight * fomrat_score + time_weight * correctness_score + length_score
    else:
        score = fomrat_score + correctness_score + length_score
    
    # return score, fomrat_score, correctness_score, length_score
    print("*"*20, "groundtruth", "*"*20)
    print(ground_truth)
    print("*"*20, "solutionstr", "*"*20)
    print(solution_str)
    print("*"*20, "score, format, correct, length", "*"*20)
    print(score, fomrat_score, correctness_score, length_score)
    return {
        "score": score,
        "fomrat_score": fomrat_score,
        "correct_score": correctness_score,
        "length_score": length_score
    }

if __name__ == '__main__':
    reward = 1
    decay_rate = 0.3
    relevance_avg = 0.454
    pd_tools = [
        # {'name': 'calculateShippingCost', 'parameters': {'dimensions': {'length': 12, 'width': 8, 'height': 6}, 'weight': 5, 'originZip': '10001', 'destinationZip': '90001', 'deliverySpeed': '3Day'}},
        {'name': 'getDeliveryReliability', 'parameters': {'originZip': '10001', 'destinationZip': '90001', 'deliverySpeed': '3Day'}}
    ]
    negative_list = [{'name': 'getDeliveryReliability', 'relevance': '0.1'}]
    negative_list = []
    negative_score = compute_negative_score(pd_tools, negative_list, decay_rate=0.5)
    print(negative_score)
    reward = (reward + negative_score) * (1 + decay_rate * (1-relevance_avg))
    print(reward)
    
