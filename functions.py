from openai import OpenAI
import openai
import re
import os
import csv
from fuzzywuzzy import fuzz
import pandas as pd
import io
import requests
import json
from typing import List, Dict, Optional, Any

api_key = os.environ['api_key']

AIRTABLE_BASE_URL = os.environ['AIRTABLE_BASE_URL']

BEARER_TOKEN = os.environ['BEARER_TOKEN']

client = OpenAI(api_key=api_key)


def extract_texts(image_urls):
  extracted_texts = []
  flag_count = 0

  for url in image_urls:
    try:
      response = client.chat.completions.create(
          model="gpt-4o",
          messages=[{
              "role":
              "user",
              "content": [{
                  "type":
                  "text",
                  "text":
                  "The attached image is of a restaurant menu. Extract menu items, their prices and their category from this restaurant menu. If category is not present, use 'All' as the default category. If the image does not resemble a restaurant menu respond with 'NO MENU FOUND', or if it is not readable respond with 'MENU NOT READABLE'."
              }, {
                  "type": "image_url",
                  "image_url": {
                      "url": url
                  }
              }]
          }],
          max_tokens=2000)
      content = response.choices[0].message.content
      if content == "NO MENU FOUND" or content == "MENU NOT READABLE":
        flag_count += 1
      else:
        extracted_texts.append(content)
    except Exception as e:
      print(f"Error processing image {url}: {e}")
      flag_count += 1

  if flag_count == len(image_urls):
    print("No menu found or menu not readable in any of the images.")
    return "FLAG"

  combined_text = "\n\n".join(extracted_texts)

  return combined_text


def get_menu_csv(combined_text):
  try:
    final_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role":
            "user",
            "content":
            f"""Following is a text file containing data about a restaurant menu. The data is extracted from multiple image files, so try to find relations between all menu items.:

      {combined_text}

      Please extract the menu items, their prices, and their categories, and format them as CSV with three columns: 'Item', 'Price', 'Vegetarian/Non-Vegetarian' and 'Category'.
      If default category 'All' is found for all items, use intelligent mapping and categorisation for all menu items based on the cuisine type, starter/main course, beverage, veg/non veg, etc. A single string value should be returned for the category.
      Give the csv within '<csv>' tags.
      Generate four columns for each item:
      'Item': Name of the Cuisine/Food Item. Example: 'Butter Chicken'
      'Price': Price of the food item (in Indian Rupees). Example: 250
      'Vegetarian/Non-Vegetarian: Whether the food item is Vegetarian or Non Vegetarian. Example: 'Non-Vegetarian'
      'Category': Category of the food item found in the Menu. If no category is mentioned, categorise it based on the type of Cuisine. Example: 'Main Course'
      """
        }],
        max_tokens=2000)

    csv_output = final_response.choices[0].message.content
    return csv_output
  except Exception as e:
    print(f"Error generating CSV: {e}")
    return None


def get_menu_df(text: str):
  match = re.search(r"<csv>\s*(.*?)\s*</csv>", text, re.DOTALL)
  if match:
    raw_csv = io.StringIO(match.group(1).strip())
    df = pd.read_csv(raw_csv)
    return df
  else:
    return None


def find_best_image_match(menu_item, image_df):
  best_score = 0
  best_match_id = None
  best_match_item = 'NA'

  for index, row in image_df.iterrows():
    score = fuzz.partial_ratio(menu_item.lower(), row['item_name'].lower())
    if score > best_score:
      best_score = score
      best_match_id = row['image_id']
      best_match_item = row['item_name']

  return best_match_id, best_match_item, best_score


def match_item_url(df, image_db):
  menu_items = df['Item']

  images = []
  matched_w = []
  score_l = []

  for item in menu_items:
    matched_image_id, best_match_item, score = find_best_image_match(
        item, image_db)

    images.append(matched_image_id)
    matched_w.append(best_match_item)
    score_l.append(score)

  df['image_url'] = pd.Series(images)
  df['Matched With'] = pd.Series(matched_w)
  df['Score'] = pd.Series(score_l)
  return df


def get_processing_tasks() -> List[Dict]:

  url = f"{AIRTABLE_BASE_URL}/ScanMenu"

  headers = {
      "Authorization": f"Bearer {BEARER_TOKEN}",
      "Content-Type": "application/json"
  }

  params = {"maxRecords": 100, "view": "Grid view"}

  processing_tasks = []
  offset = None

  try:
    while True:
      if offset:
        params["offset"] = offset

      response = requests.get(url, headers=headers, params=params)
      response.raise_for_status()

      data = response.json()
      records = data.get("records", [])

      for record in records:
        fields = record.get("fields", {})
        status = fields.get("Status", "").lower()

        if status == "processing":
          processing_tasks.append(record)

      offset = data.get("offset")
      if not offset:
        break

  except requests.exceptions.RequestException as e:
    print(f"Error fetching data from Airtable: {e}")
    return []
  except json.JSONDecodeError as e:
    print(f"Error parsing JSON response: {e}")
    return []

  return processing_tasks


def get_processing_df(list_p):
  flattened = []
  for record in list_p:
    flat = {
        'id': record['id'],
        'createdTime': record['createdTime'],
        **record['fields']
    }
    flattened.append(flat)

  df = pd.DataFrame(flattened)
  return df


def get_image_url_list(df):
  image_urls = df['image_url'].tolist()
  return image_urls


def update_task_status(task_id, new_status="completed"):
  url = f"{AIRTABLE_BASE_URL}/ScanMenu"
  try:
    params = {'filterByFormula': f"{{task_id}} = '{task_id}'"}

    response = requests.get(url,
                            headers={
                                'Authorization': f'Bearer {BEARER_TOKEN}',
                                'Content-Type': 'application/json'
                            },
                            params=params)

    if response.status_code != 200:
      print(f"Error fetching records: {response.status_code}")
      return False

    records = response.json().get('records', [])

    if not records:
      print(f"No records found for task_id: {task_id}")
      return False

    update_records = []
    for record in records:
      update_records.append({
          'id': record['id'],
          'fields': {
              'Status': new_status
          }
      })

    update_response = requests.patch(
        AIRTABLE_BASE_URL,
        headers={
            'Authorization': f'Bearer {BEARER_TOKEN}',
            'Content-Type': 'application/json'
        },
        data=json.dumps({'records': update_records}))

    if update_response.status_code == 200:
      print(
          f"Successfully updated {len(update_records)} records for task_id: {task_id}"
      )
      return True
    else:
      print(f"Error updating records: {update_response.status_code}")
      return False

  except Exception as e:
    print(f"Exception occurred: {e}")
    return False


def upload_dataframe_to_airtable(df: pd.DataFrame,
                                 api_token: str,
                                 batch_size: int = 10) -> Dict[str, Any]:

  url = f"{AIRTABLE_BASE_URL}/Products2"

  
  headers = {
      "Authorization": f"Bearer {api_token}",
      "Content-Type": "application/json"
  }

  def format_field_value(value: Any, field_name: str = "") -> Any:
    """Format field values for Airtable API"""
    if isinstance(value, (list, dict)):
      return value
    try:
      if pd.isna(value):
        return None
    except (ValueError, TypeError):
      pass

    if isinstance(value, str):
      if field_name.lower() in [
          'image', 'images', 'photo', 'photos', 'attachment', 'attachments'
      ] or 'image' in field_name.lower():
        if value.strip(): 
          return [{"url": value.strip()}]
        else:
          return []
      elif ',' in value:
        return [item.strip() for item in value.split(',')]
      else:
        return value.strip()
    else:
      return value

  def create_record_from_row(row: pd.Series) -> Dict[str, Any]:
    fields = {}
    for col in df.columns:
      if col in row.index:
        formatted_value = format_field_value(row[col], col)
        if formatted_value is not None:
          fields[col] = formatted_value

    return {"fields": fields}

  all_records = []
  for _, row in df.iterrows():
    record = create_record_from_row(row)
    all_records.append(record)

  results = {
      "success": True,
      "total_records": len(all_records),
      "uploaded_records": 0,
      "failed_batches": [],
      "responses": []
  }

  for i in range(0, len(all_records), batch_size):
    batch = all_records[i:i + batch_size]

    payload = {"records": batch}

    try:
      print(payload)
      response = requests.post(url, headers=headers, json=payload)
      response.raise_for_status()

      response_data = response.json()
      results["responses"].append(response_data)
      results["uploaded_records"] += len(batch)

      print(
          f"Successfully uploaded batch {i//batch_size + 1}: {len(batch)} records"
      )

    except requests.exceptions.RequestException as e:
      results["success"] = False

      error_details = "Unknown error"
      if hasattr(e, 'response') and e.response is not None:
        try:
          error_json = e.response.json()
          error_details = error_json.get('error', {})
          if isinstance(error_details, dict):
            error_message = error_details.get('message', 'No message')
            error_type = error_details.get('type', 'No type')
            error_details = f"Type: {error_type}, Message: {error_message}"
        except:
          error_details = e.response.text

      error_info = {
          "batch_start": i,
          "batch_size": len(batch),
          "error": str(e),
          "error_details": error_details,
          "sample_record":
          batch[0] if batch else None  
      }
      results["failed_batches"].append(error_info)
      print(f"Failed to upload batch {i//batch_size + 1}: {e}")
      print(f"Error details: {error_details}")
      print(
          f"Sample record structure: {json.dumps(batch[0] if batch else {}, indent=2)}"
      )

  return results


def upload_menu_to_menu_db(record):
  table_name = "Menus"
  airtable_url = f"{AIRTABLE_BASE_URL}/{table_name}"

  headers = {
      "Authorization": f"Bearer {BEARER_TOKEN}",
      "Content-Type": "application/json"
  }

  payload = {"records": [{"fields": record}]}

  response = requests.post(airtable_url,
                           headers=headers,
                           data=json.dumps(payload))

  if response.status_code == 200 or response.status_code == 201:
    print("Records created successfully.")
    return response.json()
  else:
    print(f"Failed to create records: {response.status_code}")
    print(response.text)
    return None
