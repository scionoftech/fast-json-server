import uvicorn
from fastapi import FastAPI, Request
from fastapi import APIRouter
from typing import Dict, Optional, Any, Tuple, List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from graphene import Schema
from glob import glob
from pathlib import Path
import pandas as pd
import json
from math import ceil
from os import sep
import graphene
from starlette.graphql import GraphQLApp
from graphql import GraphQLError


class ProjectSettings:
    PROJECT_NAME = "FAST JSON GraphQL SERVER"
    PROJECT_DESCRIPTION = "Simple GraphQL Application using JSON data and FASTAPI"
    API_VERSION = "1.0.0"
    API_VERSION_PATH = "/api/v1"


# REST API Settings
app = FastAPI(title=ProjectSettings.PROJECT_NAME,
              description=ProjectSettings.PROJECT_DESCRIPTION,
              version=ProjectSettings.API_VERSION,
              # docs_url=None,
              # redoc_url=None,
              openapi_url=f"{ProjectSettings.API_VERSION_PATH}/openapi.json",
              docs_url=f"{ProjectSettings.API_VERSION_PATH}/docs",
              redoc_url=f"{ProjectSettings.API_VERSION_PATH}/redoc")

# Middleware Settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_responses = {
    400: {"description": "Bad Request"},
    401: {"description": "Unauthorized"},
    404: {"description": "Not Found"},
    422: {"description": "Validation Error"},
    500: {"description": "Internal Server Error"}
}

general_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {
                "example": {"message": "success"}
            }
        },
    }
}

pagination_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {
                "example": {"total_pages": 0,
                            "total_items": 0,
                            "page_data": {"page_num": 0,
                                          "items_count": 0,
                                          "items": []}}
            }
        },
    }
}

api_router = APIRouter()


def create_routes(name: str) -> str:
    """
    Mutations Routes
    :param name:
    :return:
    """
    routes = '''
class Create%s(graphene.Mutation):
    """
    Create %s Record
    """

    class Arguments:
        createRecord = %sRecord(required=True)
    
    message = graphene.String()
    id = graphene.Int()
    @staticmethod
    def mutate(root, info, createRecord):

        try:
            data = jsonable_encoder(createRecord)
            data["id"] = int(%s["id"].max()) + 1
            print(data)
            column_order = list(%s.columns)
            data_new = {col:data[col] for col in column_order}

            %s.loc[len(%s.index)] = list(data_new.values())

            path = Path(str(%s_path))
            file_name = str(path.name).split(".")[0]

            %s.to_json(f"{path.parent.absolute()}{sep}{file_name}.json",orient="records",indent=4)

            return Create%s(message="success",id=data["id"])
        except Exception as e:
            print(e)
            raise GraphQLError("Internal Server Error")


class Update%s(graphene.Mutation):
    """
    Update %s Record
    """

    class Arguments:
        id = graphene.Int(required=True)
        updateRecord = %sRecord(required=True)
    
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, updateRecord):

       try:
            data = jsonable_encoder(updateRecord)
            
            %s.loc[%s['id'] == int(id), list(data.keys())] = list(data.values())

            path = Path(str(%s_path))
            file_name = str(path.name).split(".")[0]

            %s.to_json(f"{path.parent.absolute()}{sep}{file_name}.json",orient="records",indent=4)

            return Update%s(message="success")
       except Exception as e:
            print(e)
            raise GraphQLError("Internal Server Error")


class Delete%s(graphene.Mutation):
    """
    Delete %s
    """

    class Arguments:
        id = graphene.Int(required=True)

    message = graphene.String()

    @staticmethod
    def mutate(root, info, id):
        try:
            %s.drop(%s[%s['id'] == int(id)].index, inplace = True)

            path = Path(str(%s_path))
            file_name = str(path.name).split(".")[0]

            %s.to_json(f"{path.parent.absolute()}{sep}{file_name}.json",orient="records",indent=4)

            return Delete%s(message="success")
        except Exception:
            print(e)
            message = "failed"
            raise GraphQLError("Internal Server Error")

      ''' % (
        name.title(), name.title(), name.title(), name, name, name, name,
        name, name, name.title(),
        name.title(), name, name.title(), name, name, name, name,
        name.title(),
        name.title(), name, name, name, name, name, name, name.title())
    return routes


def create_mutations(mut_strs):
    """
    Mutations
    :param mut_strs:
    :return:
    """
    return '''
class Mutations(graphene.ObjectType):
    """
    GraphQL Mutations
    """
%s  
    ''' % (mut_strs)


def mutation_routes(name):
    """
    Mutations objects
    :param name:
    :return:
    """
    mut_var = '''

    create%s = Create%s.Field()
    update%s = Update%s.Field()
    delete%s = Delete%s.Field()

    ''' % (
        name.title(), name.title(), name.title(), name.title(), name.title(),
        name.title())
    return mut_var


def query_super_schema(name):
    """
    Query Data type Objects
    :param name:
    :return:
    """
    return '''
class %sPageInfo(graphene.ObjectType):    
    page_num = graphene.Int()
    item_count = graphene.Int()
    items = graphene.List(%sItems)
class %s(graphene.ObjectType):
    total_pages = graphene.Int()
    total_items = graphene.Int()
    page_data = graphene.Field(%sPageInfo)
    ''' % (name.title(), name.title(), name.title(), name.title())


def mutation_schema(name, params):
    """
    Mutation schemas
    :param name:
    :param params:
    :return:
    """
    return '''
class %sRecord(graphene.InputObjectType):
%s
    ''' % (name.title(), params)


def query_schema(name, params):
    """
    Query Data type Objects
    :param name:
    :param params:
    :return:
    """
    return '''
class %sItems(graphene.ObjectType):
%s
    ''' % (name.title(), params)


def query_params(name, params):
    """
    Query Data Types
    :param name:
    :param params:
    :return:
    """
    return '''
    %s = graphene.List(%s, %s)
    ''' % (name, name.title(), params)


def query_method(name, params, filters):
    """
    create Query Resolver
    :param name:
    :param params:
    :param filters:
    :return:
    """
    return '''  
    def resolve_%s(self, info, %s,page_size=10,page_num=1, **kwargs):

        try:
            data = %s.copy()
            total_items = data.shape[0]
            %s

            if page_size is not None:

                offset = page_size*(page_num-1)

                data = data[offset:offset + page_size]
            return [{"total_pages": ceil(data.shape[0]/float(page_size)),
                                     "total_items": total_items,
                                     "page_data": {"page_num": page_num,
                                                   "item_count": page_size,
                                                   "items":
                                                       json.loads(data.to_json(orient="records"))}}]
            # return json.loads(data.to_json(orient="records"))
        except Exception:
            print(e)
            raise GraphQLError("Internal Server Error")

    ''' % (name, params, name, filters)


def create_query(filter_vars, filter_methods):
    """
    create Query
    :param filter_vars:
    :param filter_methods:
    :return:
    """
    return '''
class Query(graphene.ObjectType):
    """
    GraphQL Query
    """

%s

%s  

    ''' % (filter_vars, filter_methods)


# Root API
@app.get(ProjectSettings.API_VERSION_PATH, include_in_schema=False)
def root() -> JSONResponse:
    return JSONResponse(status_code=200,
                        content={
                            "message": "Welcome to FAST JSON SERVER"})


source = dict()
file_paths = dict()


def get_fil_int(col) -> str:
    """
    Integer based filter conditions
    :param col:
    :return:
    """
    return """
            if %s is not None:
                data = data[data["%s"] == int(%s)]
    """ % (col, col, col)


def get_fil_non_int(col) -> str:
    """
    String based filter conditions
    :param col:
    :return:
    """
    return """
            if %s is not None:
                data = data[data["%s"] == str(%s)]
    """ % (col, col, col)


def get_fil_float(col) -> str:
    """
    floats based filter conditions
    :param col:
    :return:
    """
    return """
            if %s is not None:
                data = data[data["%s"] == float(%s)]
    """ % (col, col, col)


def graph_conf():
    """
    GraphQL configurations
    :return:
    """
    return '''
app.add_route(f"{ProjectSettings.API_VERSION_PATH}/graphql", GraphQLApp(graphiql=True, schema=graphene.Schema(query=Query, mutation=Mutations)))
# graphql_app = GraphQLApp(graphiql=True, schema=Schema(query=Query, mutation=Mutations))
# @app.api_route(f"{ProjectSettings.API_VERSION_PATH}/graphql",
#                    methods=["GET", "POST"])
# async def graphql(request: Request):
#         """
#         FastAPI-GraphQL with JWT Authentication
#         """
#         return await graphql_app.handle_graphql(request=request)
    '''


def get_query_params(df_data) -> Tuple:
    """
    Create Query / Mutation related params
    :param df_data:
    :return:
    """
    filter_str = ""
    body_params = ""
    query_body_params = ""
    # body_param_var = list()
    # body_param_val = list()
    query_filters = list()
    for col in df_data.columns:
        if df_data[col].dtype in ["int", "int32", "int64"]:
            filter_str += get_fil_int(col)
            if col != "id":
                # body_param_var.append(col)
                # body_param_val.append("graphene.Int(required=True)")
                body_params += f"\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020{col} = graphene.Int(required=True)\n"
                query_filters.append(f"{col} = graphene.Int()")
            query_body_params += f"\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020{col} = graphene.Int()\n"
        elif df_data[col].dtype in ["float", "float32", "float64"]:
            filter_str += get_fil_float(col)
            # body_param_var.append(col)
            # body_param_val.append("graphene.Float(required=True)")
            body_params += f"\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020{col} = graphene.Float(required=True)\n"
            query_filters.append(f"{col} = graphene.Float()")
            query_body_params += f"\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020{col} = graphene.Float()\n"
        else:
            filter_str += get_fil_non_int(col)
            # body_param_var.append(col)
            # body_param_val.append("graphene.String(required=True)")
            body_params += f"\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020{col} = graphene.String(required=True)\n"
            query_filters.append(f"{col} = graphene.String()")
            query_body_params += f"\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020{col} = graphene.String()\n"
    filter_params = ",".join(
        [f"{col}" for col in df_data.columns if col != "id"])
    query_filter_params = ",".join(
        [f"{col} = None" for col in df_data.columns])
    # body_params = ",".join(body_param_var) + " = " + ",".join(body_param_val)
    return filter_str, filter_params, body_params, query_filter_params, ",".join(
        query_filters + ["id = graphene.Int()", "page_size=graphene.Int()",
                         "page_num=graphene.Int()"]), query_body_params


def start_graphql(data_path: str, host: str, port: int, log_level):
    """
    Start GraphQL Server
    :param data_path:
    :param host:
    :param port:
    :param log_level:
    :return:
    """
    # Load JSON data
    for file_path in glob(f"{data_path}/*.json"):
        file = Path(file_path)
        file_name = str(file.name).split(".")[0]
        file_paths[file_name] = file_path
        source[file_name] = pd.read_json(file_path, orient="records")
        globals()[f"{file_name}_path"] = file_path
    mut_strs = ["\u0020\u0020\u0020\u0020"]
    query_params_str = ""
    query_filter_str = ""
    for key, value in source.items():
        globals()[key] = value
        filter_str, filter_params, body_params, query_filter_params, query_filters_str, query_body_params = get_query_params(
            value)
        # create mutations schemas
        exec(mutation_schema(key, query_body_params), globals())
        # exec(create_routes(str(key), filter_params, body_params),
        #      globals())

        # create Mutation routes
        exec(create_routes(str(key)), globals())

        # create Query Schemas
        exec(query_schema(key, query_body_params), globals())

        # create Query schemas
        exec(query_super_schema(key), globals())
        mut_strs.append(mutation_routes(key).strip())
        query_params_str += query_params(key, query_filters_str)
        query_filter_str += query_method(key, query_filter_params, filter_str)
    # create Mutations
    exec(create_mutations("\n\u0020\u0020\u0020\u0020".join(mut_strs)),
         globals())
    # create Query
    exec(create_query(f"\t{query_params_str}", f"\t{query_filter_str}"),
         globals())
    # create GraphQL Configuration
    exec(graph_conf(), globals())

    # Run Server
    uvicorn.run(app, host=host, port=port, log_level=log_level)
