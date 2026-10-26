"""Convert raw multi-turn trajectories into normalized PLAN-TOOL records."""

# SPDX-License-Identifier: CC-BY-NC-4.0

import argparse
import ast
import json

from tqdm import tqdm

def toolParsing(tools:str):
  tools = json.loads(tools)
  tool_string = ""
  for t in range(len(tools)):
    current_tool_string = str(t+1) + ". Name: " + tools[t]["name"] + "\n"
    current_tool_string = current_tool_string + "Description: " + tools[t]["description"] + "\n"
    current_tool_string = current_tool_string + "Parameters: " + json.dumps(tools[t]["parameters"]) + "\n"
    current_tool_string = current_tool_string + "Required: " + json.dumps(tools[t]["required"]) + "\n"
    tool_string = tool_string + current_tool_string
  return tool_string, len(tools)

def instructionParsing(system_content):
  instruction = "You are a helpful multi-turn dialogue assistant capable of leveraging tool calls to solve user tasks and provide structured chat responses.\n\n**Available Tools**\nIn your response, you can use the following tools:\n"
  tool_string, tools_num = toolParsing(system_content.split("<tool>")[1].split("</tool>")[0])
  instruction = instruction + tool_string
  ending = "\n**Steps for Each Turn**\n1. **plan:** Recall relevant context and analyze the current user goal.\n2. **Decide on Tool Usage:** If a tool is needed, specify the tool and its parameters.\n3. **Respond Appropriately:** If a response is needed, generate one while maintaining consistency across user queries.\n\n**Output Format**\n```plaintext\n<plan> Your thoughts and reasoning </plan>\n<tool_call>\n{\"name\": \"Tool name\", \"parameters\": {\"Parameter name\": \"Parameter content\", \"... ...\": \"... ...\"}}\n{\"name\": \"... ...\", \"parameters\": {\"... ...\": \"... ...\", \"... ...\": \"... ...\"}}\n...\n</tool_call>\n<response> AI's final response </response>\n```\n\n**Important Notes**\n1. You must always include the `<plan>` field to outline your reasoning. Provide at least one of `<tool_call>` or `<response>`. Decide whether to use `<tool_call>` (possibly multiple times), `<response>`, or both.\n2. You can invoke multiple tool calls simultaneously in the `<tool_call>` fields. Each tool call should be a JSON object with a \"name\" field and an \"parameters\" field containing a dictionary of parameters. If no parameters are needed, leave the \"parameters\" field an empty dictionary.\n3. Refer to the previous dialogue records in the history, including the user's queries, previous `<tool_call>`, `<response>`, and any tool feedback noted as `<obs>` (if exists)."
  instruction = instruction + ending
  return instruction, tools_num

def outputParsing(content, content_type):
  if content_type == "assistant":
    if "<call>" in content:
      plan_str = content.split("<call>")[0]
      if "<plan>" in plan_str:
        plan_str = plan_str.split("<plan>")[1].split("</plan>")[0]
        output_string = "<plan> " + plan_str + " </plan>" + "\n"
      try:
        tool_str = content.split("</plan>")[1]
      except:
        tool_str = content.split("<call>")[1]
      if "<call>" in str(tool_str):
        tool_str = tool_str.split("<call>")[1].split("</call>")[0].replace("true","True").replace("false","False").replace('null', 'None')
      else:
        tool_str = tool_str.split("</call>")[0].replace("true","True").replace("false","False").replace('null', 'None')
      tools = ast.literal_eval(str(tool_str))
      tools_final = "<tool_call>"
      for t in tools:
        t["parameters"] = t.pop("arguments")
        tools_final = tools_final + json.dumps(t) + "\n"
      tools_final = tools_final + "</tool_call>"
      # print('#'*100)
      # print(tools_final)
      output_string = output_string + tools_final + "\n"
      return output_string

    if "<final>" in content:
      plan_str = content.split("<plan>")[1].split("</plan>")[0]
      plan_str = "<plan> " + plan_str + " </plan>" + "\n"
      response_str = content.split("<final>")[1].split("</final>")[0]
      output_string = plan_str + "<response> " + response_str + " </response>" + "\n"
      return output_string

def inputParsing(input_string, content, content_type):
  if content_type == "tool":
    # print('#'*100)
    # print("content:", content)
    content = json.loads(content)
    obs_string = "<obs> ["
    for t in content:
      t["parameters"] = t.pop("arguments")
      obs_string = obs_string + json.dumps(t) + "\n"
    obs_string = obs_string + "] </obs> \n"
    return  input_string + "\n" + obs_string + "\n"
  if content_type == "assistant":
    if "<call>" in content:
      plan_str = content.split("<plan>")[1].split("</plan>")[0]
      input_string = input_string + "<plan> " + plan_str + " </plan>" + "\n"
      try:
        tool_str = content.split("</plan>")[1]
      except:
        tool_str = content.split("<call>")[1]
      if "<call>" in str(tool_str):
        tool_str = tool_str.split("<call>")[1].split("</call>")[0].replace("true","True").replace("false","False").replace('null', 'None')
      else:
        tool_str = tool_str.split("</call>")[0].replace("true","True").replace("false","False").replace('null', 'None')

      # tool_str = content.split("<call>")[1].split("</call>")[0].replace("true","True").replace("false","False").replace('null', 'None')

      tools = ast.literal_eval(str(tool_str))
      tools_final = "<tool_call> ["
      for t in tools:
        t["parameters"] = t.pop("arguments")
        tools_final = tools_final + json.dumps(t)
      tools_final = tools_final + "] </tool_call>"
      input_string = input_string + tools_final + "\n"
      return input_string
  if content_type == "user":
    input_string = input_string + "<user> " + content + " </user>\n"
    return input_string
  else:
    return input_string

def toolStepCounter(data_dict):
  toolcount = 0
  for i in data_dict:
    if i["role"] == "assistant":
      toolcount = toolcount + 1
  return toolcount

def messageSeperator(messages, trajectoryID):
  messages = messages["messages"]
  seperateCounters = []
  for i in range(len(messages)):
    if messages[i]["role"] == "assistant":
      seperateCounters.append(i)
  seperated_messages = []
  toolCount = toolStepCounter(messages)
  for s in seperateCounters:
    new_message = {}
    new_message["messages"] = messages[:s+1]
    new_message["trajectoryID"] = trajectoryID
    new_message["totalToolCount"] = toolCount
    new_message["finalAnswer"] = "True" if s+1 == len(messages) else "False"
    seperated_messages.append(new_message)
  return seperated_messages

def singleMassageProcessing(message):
  toolCount = toolStepCounter(message["messages"])
  data_dic = {}
  data_dic["trajectoryID"] = message["trajectoryID"]
  data_dic["currentToolCount"] = toolCount
  data_dic["totalToolCount"] = message["totalToolCount"]
  data_dic["finalAnswer"] = message["finalAnswer"]
  input_string = "**Dialogue Records History**\n"
  tools_num = 0
  negative_num = 0
  for i in range(len(message["messages"])):
    if message["messages"][i]["role"] == "system":
      data_dic["instruction"], tools_num = instructionParsing(message["messages"][i]["content"])
    elif i+1 == len(message["messages"]) and message["messages"][i]["role"] == "assistant":
      # print('#'*100)
      # print(i, len(message["messages"]))
      # print(message["messages"][i]["content"]["groundtruth"])
      data_dic["output"] = outputParsing(message["messages"][i]["content"]["groundtruth"], "assistant")
      if str(data_dic["output"]) == "None":
        continue
      data_dic["negative"] = json.dumps(message["messages"][i]["content"].get("negative", []))
      negative_num = len(message["messages"][i]["content"]["negative"])
      # print('#'*100)
      # print(negative_num, tools_num)
      # print(data_dic["negative"])
      # print('-'*100)
      # print(message)
      # assert negative_num > 0 and tools_num > 0 and negative_num == tools_num
      # pre-check
      ans = data_dic["output"]
      if "<tool_call>" in ans:
        # print('#'*100)
        # print(ans)
        gt_tool_call = ans.split("<tool_call>")[1].split("</tool_call>")[0].strip()
        # print('#'*100)
        # print(gt_tool_call)
        gt_tools = gt_tool_call.split("\n")
        # print('#'*100)
        # print(gt_tools)
        gt_tools = [json.loads(tool) for tool in gt_tools]
        # print('#'*100)
        # print(gt_tools)

    else:
      # print('#'*100)
      # print(message["messages"][i]['role'])
      # is_user = (message["messages"][i]['role'] == "user")
      # has_user = '<user>' in input_string and '</user>' in input_string
      # if is_user and has_user:
      #     continue
      # else:
      content = message["messages"][i]["content"]
      if message["messages"][i]["role"] == "assistant":
          content = content["groundtruth"]
      # print('#'*100)
      # print(is_user, has_user)
      # print(input_string)
      input_string = inputParsing(input_string, content, message["messages"][i]['role'])
      # print('#'*100)
      # print(input_string)
  data_dic["input"] = input_string
  return data_dic

def massageProcessing(content, trajectoryID):
  messages = messageSeperator(content, trajectoryID)
  data = []
  for m in messages:
    # print('#'*100)
    # print(m)
    data.append(singleMassageProcessing(m))
  return data

# def read_jsonl_file(filepath):
#   data = []
#   with open(filepath, 'r', encoding='utf-8') as f:
#     counter = 0 
#     for line in tqdm(f):
#       if counter >1:
#         break
#       data_json = json.loads(line.strip())  # 移除换行符后解析JSON
#       # 处理字典数据（示例）
#       # print(data.keys())
#       # print(len(data['messages']))
#       data_list = massageProcessing(data_json, counter)
#       data = data + data_list
#       counter += 1
#   print(json.dumps(data))
#   return data

import json
from tqdm import tqdm

def read_jsonl_file(filepath):
    data = []
    error_count = 0  # 用于统计报错数目

    with open(filepath, 'r', encoding='utf-8') as f:
        counter = 0
        for line in tqdm(f):
            # if counter >= 3:
            #     print('\n')
            #     print(json.dumps(data))
            #     break
            # counter += 1

            # # 尝试解析当前行的 JSON 数据
            # data_json = json.loads(line.strip())  # 移除换行符后解析JSON
            
            # # 调用 massageProcessing 方法处理数据
            # data_list = massageProcessing(data_json, counter)
            
            # # 如果正常处理，将结果追加到 data 中
            # data = data + data_list

            try:
                counter += 1

                # 尝试解析当前行的 JSON 数据
                data_json = json.loads(line.strip())  # 移除换行符后解析JSON
                
                # 调用 massageProcessing 方法处理数据
                data_list = massageProcessing(data_json, counter)
                
                # output 有 None 的剔除
                for i in data_list:
                  if i["output"] == "None" or i["output"] == None:
                    print(i)
                    raise Exception
                
                # 如果正常处理，将结果追加到 data 中
                data = data + data_list

            except Exception as e:
                # 捕获任何异常，并打印错误信息
                error_count += 1
                print(f"[ERROR] Error processing index-{counter}: {e}")
    
    data.sort(key=lambda x: x["totalToolCount"])
    print(f"Data processing completed. Total errors: {error_count}")
    return data

def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--input-file", required=True, help="Raw trajectory JSONL file")
  parser.add_argument("--output-file", required=True, help="Normalized JSON output file")
  args = parser.parse_args()

  data = read_jsonl_file(args.input_file)
  with open(args.output_file, "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)
  print(f"Saved {len(data)} records to {args.output_file}")


if __name__ == "__main__":
  main()
