25.07 
Користувачі можуть завантажувати світлини з описом (POST).
Користувачі можуть видаляти світлини (DELETE).
Користувачі можуть редагувати опис світлини (PUT).
Користувачі можуть отримувати світлину за унікальним посиланням (GET).

В БД буде таблиця (POST):
ID
image url
description
is_deleted(false)
created_at
updated_at
user_id

Table Tag
ID
Name
created_at
updated_at

MM PostTag
ID
Post_ID
Tag_ID

ID Post_ID Tag_ID
1 1 1
2 1 2
3 1 3
4 1 4
5 1 5

Results:
Tables created tomorrow continue to write routes


26.07
Results: created route for post posts

Next time: -save payload to DB
-fix cloudinary upload process

2.08
Result: Created repository posts and saved to DB
Next time: solve problem with cloudinary 

13.09
Result: fixed  issues with images on cloudinary 
Next steps: update technical requirements

27.09
Result: Implemented Delete Post IT
Next step: fix bug with delete implement update operation on colum is_delete

03.10
Result: Fixed bug where delete method delete data from DB
Implemented update method 
Next step: implement method where users can get picture by ID

04.10
Result: implemented method where users can get post by ID and list of all posts by the user in descending order
Next steps: Implement up to 5 tags under posts

10.10 
