[fast-json-server v0.0.1](https://pypi.org/project/fast-json-server/)

**fast-json-server** provides a full **REST API / GraphQL** Server with zero
coding in few seconds.

fast-json-server provides a simple and quick back-end for development.

fast-json-server only requires json data.

## Installation

```shell
$ pip install fast-json-server
```

## How to use

Create individual json files with some data in a folder

**Note:** json objects must contain **id** key.

#### /sample_data/users.json

```json

[
  {
    "id": 1,
    "first_name": "Sampath",
    "last_name": "Varma"
  },
  {
    "id": 2,
    "first_name": "Virat",
    "last_name": "Ranbhor"
  },
  {
    "id": 3,
    "first_name": "Rakesh",
    "last_name": "Chopra"
  }
]

```

#### /sample_data/articles.json

```json

[
  {
    "id": 1,
    "title": "Article1",
    "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore, et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    "likes": 20,
    "created_date": "11/30/2021",
    "author_id": 3
  },
  {
    "id": 2,
    "title": "Article2",
    "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    "likes": 20,
    "created_date": "11/30/2021",
    "author_id": 2
  },
  {
    "id": 3,
    "title": "Article3",
    "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    "likes": 20,
    "created_date": "11/30/2021",
    "author_id": 2
  }
]

```

### Start Fast-JSON-Server

fast-json-server supports REST API and GraphQL

```shell
python -m fast_json_server.json_server --data_path="/sample_data" --host="0.0.0.0" --port=3000 --log_level="debug" --server_type="rest_api"
# or
python -m fast_json_server.json_server --data_path="/sample_data" --host="0.0.0.0" --port=3001 --log_level="debug" --server_type="graph_ql" 
```

or

```python
from fast_json_server.json_server import start_server

start_server(data_path="/sample_data", host="0.0.0.0", port=3000,
             log_level='debug', server_type="rest_api")
# or
start_server(data_path="/sample_data", host="0.0.0.0", port=3000,
             log_level='debug', server_type="graph_ql")
```

## REST API Server

fast-json-server creates GET,POST,PUT,DELETE Routes from json files content.

### User routes

```
GET    /api/v1/users?page_num=1&page_size=5
GET    /api/v1/users?id=&first_name=&last_name=
POST   /users
PUT    /users/1
DELETE /users/1
```

### Article routes

```
GET    /api/v1/articles?page_num=1&page_size=5
GET    /api/v1/articles?id=&title=&content=&likes&author_id=
POST   /articles
PUT    /articles/1
DELETE /articles/1
```

Example GET Request

```shell
curl --location --request GET 'http://localhost:3000/api/v1/users?page_num=1&page_size=5'
```

Example GET Response

```json
{
  "total_pages": 1,
  "total_items": 9,
  "page_data": {
    "page_num": 1,
    "item_count": 5,
    "items": [
      {
        "id": 2,
        "first_name": "Sampath",
        "last_name": "Varma"
      },
      {
        "id": 3,
        "first_name": "Virat",
        "last_name": "Ranbhor"
      },
      {
        "id": 4,
        "first_name": "Rakesh",
        "last_name": "Chopra"
      },
      {
        "id": 5,
        "first_name": "Jimmy",
        "last_name": "Kapoor"
      },
      {
        "id": 6,
        "first_name": "Satya",
        "last_name": "Ellapragada"
      }
    ]
  }
}
```

fast-json-api provides interactive swagger api docs

```
/api/v1/docs
```

## GraphQL

fast-json-server creates the Query and Mutations from json files content.

GraphQL endpoint **/api/v1/graphql**

### User Query

```shell
# User data pagination
{
	users(pageSize:3,pageNum:1){
        totalPages,
        totalItems,
        pageData{
            pageNum,
            itemCount,
            items{
                firstName,
                lastName
            }
        },
    }
}
# User data with filter
{
	users(pageSize:3,pageNum:1,firstName:"Virat"){
        totalPages,
        totalItems,
        pageData{
            pageNum,
            itemCount,
            items{
                firstName,
                lastName
            }
        },
    }
}
```

### User Mutations

```shell
# create a record
mutation {
  createUsers(createRecord:{firstName:"Mohan",lastName:"Kumar"}) {
    message
    id
  }    
}
# update a record
mutation {
  updateUsers(id:10,updateRecord:{firstName:"Mohan",lastName:"Chandra"}) {
    message
  }    
}
# delete a record
mutation {
  deleteUsers(id:10) {
    message
  }    
}
```

### Article Query

```shell
# Articles data pagination
{
	articles(pageSize:3,pageNum:1){
        totalPages,
        totalItems,
        pageData{
            pageNum,
            itemCount,
            items{
                firstName,
                lastName
            }
        },
    }
}
# Articles data with filter
{
	articles(pageSize:3,pageNum:1,title:"Article3"){
        totalPages,
        totalItems,
        pageData{
            pageNum,
            itemCount,
            items{
                title,
                content
                likes
            }
        },
    }
}
```

### Article Mutations

```shell
# create a record
mutation {
  createArticles(createRecord:{title:"Article10",content:"Kumar","likes":0,"author_id":1}) {
    message
    id
  }    
}
# update a record
mutation {
  updateArticles(id:10,updateRecord:{title:"Article10",content:"Kumar","likes":0,"author_id":1}) {
    message
  }    
}
# delete a record
mutation {
  deleteArticles(id:10) {
    message
  }    
}
```

**Note**: All the data changes will be automatically saved to the json files.

## License

MIT