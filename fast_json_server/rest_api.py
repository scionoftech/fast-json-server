import uvicorn
from fastapi import FastAPI
from fastapi import APIRouter
from typing import Dict, Optional, Any, Tuple, List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from glob import glob
from pathlib import Path
import pandas as pd
import json
from math import ceil
from os import sep


class ProjectSettings:
    PROJECT_NAME = "FAST JSON API SERVER"
    PROJECT_DESCRIPTION = "Simple RESTAPI Application using JSON data and FASTAPI"
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


def create_routes(name: str, filter_str: str, filter_params: str) -> str:
    """
    Create Rest API Routes
    :param name:
    :param filter_str:
    :param filter_params:
    :return:
    """
    routes = '''
router = APIRouter()
@router.post("/", responses=general_responses)
def create_%s(object: %sModel) -> JSONResponse:
    """ create a %s """
    try:
        data = jsonable_encoder(object)
        data["id"] = int(%s["id"].max()) + 1
        
        column_order = list(%s.columns)
        data_new = {col:data[col] for col in column_order}
        
        %s.loc[len(%s.index)] = list(data_new.values())
        
        path = Path(str(%s_path))
        file_name = str(path.name).split(".")[0]
    
        %s.to_json(f"{path.parent.absolute()}{sep}{file_name}.json",orient="records",indent=4)
        
        return JSONResponse(status_code=200,
                        content={"message": "success"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                        content={"message": "Something Went Wrong"})


@router.put("/{id}", responses=general_responses)
def update_%s(id: str,object:%sModel) -> JSONResponse:
    """ update a %s """
    try:
        data = jsonable_encoder(object)
       
        %s.loc[%s['id'] == int(id), list(data.keys())] = list(data.values())
       
        path = Path(str(%s_path))
        file_name = str(path.name).split(".")[0]
    
        %s.to_json(f"{path.parent.absolute()}{sep}{file_name}.json",orient="records",indent=4)
    
        return JSONResponse(status_code=200,
                            content={"message": "success"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                        content={"message": "Something Went Wrong"})


@router.delete("/{id}",
               responses=general_responses)
def delete_%s(id: str) -> JSONResponse:
    """ Delete a %s """
    try:
        %s.drop(%s[%s['id'] == int(id)].index, inplace = True)
        
        path = Path(str(%s_path))
        file_name = str(path.name).split(".")[0]
        
        %s.to_json(f"{path.parent.absolute()}{sep}{file_name}.json",orient="records",indent=4)
        
        return JSONResponse(status_code=200,
                            content={"message": "success"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                        content={"message": "Something Went Wrong"})

@router.get("/", responses=pagination_responses)
def get_%s(%s, page_num: int = 1, page_size:int = 10) -> JSONResponse:
    """ Return %s"""
    try:
        data = %s.copy()
        total_items = data.shape[0]
        %s
        
        if page_size is not None:
        
            offset = page_size*(page_num-1)
            
            data = data[offset:offset + page_size]
        
        if data.shape[0] != 0:
            return JSONResponse(status_code=200, content={"total_pages": ceil(data.shape[0]/float(page_size)),
                                     "total_items": total_items,
                                     "page_data": {"page_num": page_num,
                                                   "item_count": page_size,
                                                   "items":
                                                       json.loads(data.to_json(orient="records"))}})
        else:
            return JSONResponse(status_code=404, content={"No Data Found"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                        content={"message": "Something Went Wrong"})
                        
api_router.include_router(router, prefix="/%s", tags=["%s"])
      ''' % (
        name, name, name, name, name, name, name, name, name, name, name, name,
        name, name, name, name, name, name, name,
        name, name, name, name, name,
        filter_params,
        name, name, filter_str,
        name, name)
    return routes


# Root API
@app.get(ProjectSettings.API_VERSION_PATH, include_in_schema=False)
def root() -> JSONResponse:
    """
    Root Route
    :return:
    """
    return JSONResponse(status_code=200,
                        content={
                            "message": "Welcome to FAST JSON SERVER"})


source = dict()
file_paths = dict()


def get_body_model(name, params: str):
    """
    POST / PUT Request Body Schema
    :param name:
    :param params:
    :return:
    """
    body_model = """
class %sModel(BaseModel):
%s
    """ % (name, params)
    exec(body_model, globals())


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
    Float based filter conditions
    :param col:
    :return:
    """
    return """
        if %s is not None:
            data = data[data["%s"] == float(%s)]
    """ % (col, col, col)


def get_query_params(data_name, df_data) -> Tuple:
    """
    Query Params for GET Routes
    :param data_name:
    :param df_data:
    :return:
    """
    filter_str = ""
    body_params = ""
    for col in df_data.columns:
        if df_data[col].dtype in ["int", "int32", "int64"]:
            filter_str += get_fil_int(col)
            if col != "id":
                body_params += f"\t{col}:int\n"
        elif df_data[col].dtype in ["float", "float32", "float64"]:
            filter_str += get_fil_float(col)
            body_params += f"\t{col}:float\n"
        else:
            filter_str += get_fil_non_int(col)
            body_params += f"\t{col}:str\n"
    get_body_model(data_name, body_params)
    filter_params = ",".join(
        [f"{col}:Optional[Any] = None" for col in df_data.columns])
    return filter_str, filter_params


def start_api(data_path: str, host: str, port: int, log_level):
    """
    Start REST API Server
    :param data_path:
    :param host:
    :param port:
    :param log_level:
    :return:
    """
    # Load JSON Data
    for file_path in glob(f"{data_path}/*.json"):
        file = Path(file_path)
        file_name = str(file.name).split(".")[0]
        file_paths[file_name] = file_path
        source[file_name] = pd.read_json(file_path, orient="records")
        globals()[f"{file_name}_path"] = file_path
    for key, value in source.items():
        globals()[key] = value
        filter_str, filter_params = get_query_params(key, value)
        # print(create_routes(str(key), filter_str, filter_params))
        exec(create_routes(str(key), filter_str, filter_params), globals())
    app.include_router(api_router, prefix=ProjectSettings.API_VERSION_PATH)
    uvicorn.run(app, host=host, port=port, log_level=log_level)
