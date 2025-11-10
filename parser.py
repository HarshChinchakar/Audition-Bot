import json
import os

def load_json_file(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File not found: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_section(title, content):
    output = [f"{title.upper()}\n" + "-" * len(title)]
    for sub_metric, details in content.items():
        score = details.get("score", "N/A")
        rationale = details.get("rationale", "No rationale provided.")
        improvement = details.get("improvement", "No improvement suggested.")
        
        output.append(f"\n{sub_metric} (Score: {score}/10)")
        output.append(f"Rationale   : {rationale}")
        output.append(f"Improvement : {improvement}")
    return "\n".join(output)

def parse_json_to_text(data):
    text_sections = []
    for main_section, sub_metrics in data.items():
        section_text = format_section(main_section, sub_metrics)
        text_sections.append(section_text)
    return "\n\n".join(text_sections)

def save_to_txt(text, json_path):
    base_name = os.path.splitext(os.path.basename(json_path))[0]
    output_file = base_name + "_parsed.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    return output_file

# Run this as a standalone script
if __name__ == "__main__":
    json_path = input("Enter path to the analysis JSON file: ").strip()

    try:
        data = load_json_file(json_path)
        formatted_text = parse_json_to_text(data)
        output_file = save_to_txt(formatted_text, json_path)
        print(f"\n✅ Parsed text saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error: {e}")
