import pandas as pd

image_data = {
  "image_id": ['https://sinfullyspicy.com/wp-content/uploads/2014/07/1200-by-1200-images-2.jpg', 'https://sugarspunrun.com/wp-content/uploads/2025/04/Butter-chicken-1-of-1.jpg', 'https://www.seriouseats.com/thmb/DbQHUK2yNCALBnZE-H1M2AKLkok=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/chicken-tikka-masala-for-the-grill-recipe-hero-2_1-cb493f49e30140efbffec162d5f2d1d7.JPG',
               'https://easyindiancookbook.com/wp-content/uploads/2023/06/chicken-biryani.jpg', 'https://easyindiancookbook.com/wp-content/uploads/2023/06/chicken-biryani.jpg', 'https://i.ytimg.com/vi/Do7ZdUodDdw/maxresdefault.jpg',
               'https://www.indianhealthyrecipes.com/wp-content/uploads/2022/08/chicken-korma-recipe.jpg', 'https://bhojmasale.com/cdn/shop/articles/shahi-mutton-korma-recipe-764937_1024x1024.webp?v=1739152907', 'https://i.ytimg.com/vi/ZqkcrV326WY/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLAip-TOl9jJKv0sUy71i5wku8GFqQ',
               'https://i.ytimg.com/vi/aAy3nW9SiPA/maxresdefault.jpg', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRH7iOtLYaURxBodp-mXROuIKOua-835Wsdnw&s', 'https://c.ndtvimg.com/2020-01/op8grfc_fish_625x300_11_January_20.jpg',
               'https://www.kannammacooks.com/wp-content/uploads/schezwan-veg-fried-rice-1.jpg', 'https://recipesbyclare.com/assets/images/1747914839007-45kxrtq5.webp', 'https://i0.wp.com/freshprotino.com/wp-content/uploads/2021/03/paplet-1.jpg',
               'https://www.cafegoldenfeast.com/wp-content/uploads/2025/01/Chicken-Lollipop.jpg', 'https://images.getrecipekit.com/20240103192542-buffalo-chicken-wings.jpg?aspect_ratio=1:1&quality=90&', 'https://hips.hearstapps.com/hmg-prod/images/delish-190808-baked-drumsticks-0217-landscape-pf-1567089281.jpg',
               'https://www.ndtv.com/cooks/images/chicken.seekh.jpg', 'https://c.ndtvimg.com/2020-01/a39okhfk_620_625x300_21_January_20.jpg', 'https://i.ytimg.com/vi/uCyZyYPox84/maxresdefault.jpg', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRf9tC5sOxSUzsCHVLWLjMY7HnphyZe_HiDhw&s',
               'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRL8oF7lCNZ-nsc-q6g6SZ5t_gDU024h8sM5w&s', 'https://i.ytimg.com/vi/UAOPr-hx6as/maxresdefault.jpg', 'https://myfoodstory.com/wp-content/uploads/2021/09/kadai-chicken-1.jpg', 'https://atanurrannagharrecipe.com/wp-content/uploads/2023/01/Chicken-Changezi-Photo-01.jpg',
               'https://i.ytimg.com/vi/gSW3CWcsco0/maxresdefault.jpg', 'https://theyummydelights.com/wp-content/uploads/2019/11/chicken-bhuna-masala.jpg', 'https://www.foodandwine.com/thmb/8YAIANQTZnGpVWj2XgY0dYH1V4I=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/spicy-chicken-curry-FT-RECIPE0321-58f84fdf7b484e7f86894203eb7834e7.jpg',
               'https://theyummydelights.com/wp-content/uploads/2021/12/chicken-chettinad-1.jpg', 'https://www.indianhealthyrecipes.com/wp-content/uploads/2024/02/chicken-kathi-roll-chicken-frankie.jpg',
               'https://www.indianhealthyrecipes.com/wp-content/uploads/2024/02/chicken-kathi-roll-chicken-frankie.jpg', 'https://www.indianhealthyrecipes.com/wp-content/uploads/2024/02/chicken-kathi-roll-chicken-frankie.jpg',
               'https://www.bigbasket.com/media/uploads/recipe/w-l/3684_1_1.jpg', 'https://www.indianhealthyrecipes.com/wp-content/uploads/2024/02/chicken-kathi-roll-chicken-frankie.jpg', 'https://www.thespruceeats.com/thmb/UnVh_-znw7ikMUciZIx5sNqBtTU=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/steamed-momos-wontons-1957616-hero-01-1c59e22bad0347daa8f0dfe12894bc3c.jpg',
               'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTVPvcZIxeA9bZukK18CymY32OqFUTVbkKXgQ&s',

               ],
  "item_name": [
      "Tandoori Chicken", "Butter Chicken", "Chicken Tikka Masala", "Chicken Biryani",
      "Mutton Biryani", "Vegetable Biryani",
      "Chicken Korma", "Mutton Korma", "Fish Curry",
      "Prawn Curry", "Crab Curry", "Fish Fry", "Veg Fried Rice",
      "Chicken Fried Rice", "Pomfret Tawa Fry", "Chicken Lollipop", "Chicken Wings", "Chicken Drumsticks",
      "Chicken Seekh Kebab", "Mutton Seekh Kebab","Prawn Tikka", "Paneer Tikka",
      "Chicken Afghani", "Mutton Afghani",
      "Chicken Kadhai", "Chicken Changezi", "Mutton Changezi",
      "Chicken Bhuna", "Chicken Curry",
      "Chicken Chettinad", "Chicken Roll", "Chicken Kathi Roll", "Chicken Shawarma", "Egg Kathi Roll",
      "Chicken Frankie", "Momos", "Noodles",
  ]
}
images_df = pd.DataFrame(image_data)
