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
from typing import List, Dict, Optional
from functions import extract_texts, get_menu_csv, get_menu_df, find_best_image_match, match_item_url, get_processing_tasks, get_processing_df, get_image_url_list, update_task_status, upload_dataframe_to_airtable, upload_menu_to_menu_db
from data import images_df

api_key = os.environ['api_key']

AIRTABLE_BASE_URL = os.environ['AIRTABLE_BASE_URL']

BEARER_TOKEN = os.environ['BEARER_TOKEN']

client = OpenAI(api_key=api_key)

print('Step-1: Fetching processing tasks from Airtable Base.')

df_processing = get_processing_df(get_processing_tasks())
print(f'-----> Fetched tasks. Total {len(df_processing)} tasks fetched.')
ids = df_processing['id'].tolist()
task_ids = df_processing['task_id'].tolist()
menu_id = df_processing['menu_id'][0]
outlet_id = df_processing['outlet_id'][0]
menu_name = df_processing['MenuName'][0]

if menu_name:
  pass
else:
  menu_name = 'Menu 1'

print(f'-----> Task Ids: {task_ids}')
print(f'-----> Menu Id: {menu_id}')
print(f'-----> Outlet Id: {outlet_id}')

image_urls = get_image_url_list(df_processing)
print(f'-----> Image URLs: {image_urls}')

print('Step-2: Extracting Menu Data from image URLs.')
extracted_text = extract_texts(image_urls)
print('-----> Extracted Menu Data.')
csv = get_menu_csv(extracted_text)
df = get_menu_df(csv)

print('Step-3: Matching Menu Items with Image URLs.')
df_w_images = match_item_url(df, images_df)

df_w_images['menu_id'] = menu_id
df_w_images['Outlet_ID'] = outlet_id
##

print('Step-4: Creating Out Menu DF')
out_menu_df = df_w_images[[
    'Item', 'Price', 'image_url', 'Vegetarian/Non-Vegetarian', 'Category',
    'menu_id', 'Outlet_ID'
]]

out_menu_df['Product_ID'] = df_w_images.apply(
    lambda row: str(row['menu_id']) + '00' + str(row.name), axis=1)

out_menu_df = out_menu_df[[
    'Product_ID', 'Item', 'Price', 'Outlet_ID', 'image_url',
    'Vegetarian/Non-Vegetarian', 'Category', 'menu_id'
]]
out_menu_df = out_menu_df.rename(
    columns={
        'Product_ID': 'Product_ID',
        'Item': 'Name',
        'Price': 'Price',
        'Outlet_ID': 'Outlet_ID',
        'image_url': 'Image',
        'Vegetarian/Non-Vegetarian': 'category1',
        'Category': 'category2',
        'menu_id': 'menu_id'
    })
print(f'-----> Out Menu DF Created with length {len(out_menu_df)}.')

custom_mapping = {
    'Product_ID': 'Product_ID',
    'Name': 'Item',
    'Price': 'Price',
    'Outlet_ID': 'Outlet_ID',
    'category1': 'category1',
    'category2': 'category2',
    'menu_id': 'menu_id'
}

print('Step-5: Uploading Menu Data to Airtable.')
results = upload_dataframe_to_airtable(out_menu_df, BEARER_TOKEN, batch_size=5)
print('-----> Menu Items uploaded to Airtable.')

print('Step-6: Updating Task Status in Airtable.')

for task_id in task_ids:
  print(task_id)
  update_task_status(task_id, new_status="complete")

print('-----> Task status updated in Airtable.')

print('Uploading Menu to Menu DB')
record = {'menu_id': menu_id, 'outlet_id': outlet_id, 'Menu Name': menu_name}
upload_menu_to_menu_db(record)
print('-----> Menu uploaded to Menu DB.')
print('+' * 50)
print('HO GYA BHAI')
