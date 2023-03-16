import json
import yaml
from yaml.loader import SafeLoader
from google.oauth2 import service_account
from google.cloud import functions_v2

# open and read yaml file
with open("functionGen2Build.yaml") as f:
    data = yaml.load(f, Loader=SafeLoader)

# get GCP auth credentials
with open(data["service_account_key"]) as service_key:
    info = json.load(service_key)
credentials = service_account.Credentials.from_service_account_info(info)

# create client for functions_v2
client = functions_v2.FunctionServiceClient(credentials=credentials)

# set project parent
parent = "projects/"+data["project_id"]+"/locations/"+data["location"]

# set storage source
bucket_name = data["storageSource"]["bucket_name"]
object_name = data["storageSource"]["object_name"]
storage_source = functions_v2.types.StorageSource(bucket=bucket_name, object_=object_name)
source = functions_v2.types.Source(storage_source=storage_source)

# build config
build_config_dict = {"build":data["buildConfig"]["build_name"], "runtime":data["buildConfig"]["runtime"],
"entry_point":data["buildConfig"]["entry_point"], "source":source}
build_config = functions_v2.types.BuildConfig(build_config_dict)

# build service config
service = "locations/"+data["location"]+"/services/"+data["serviceConfig"]["service_name"]
service_config_dict = {"service":service, "timeout_seconds":data["serviceConfig"]["timeout_seconds"],
"available_memory":data["serviceConfig"]["available_memory"]}

# set function
function_name = "projects/"+data["project_id"]+"/locations/"+data["location"]+"/functions/"+data["function"]["function_name"]
function_env = functions_v2.types.Environment(data["function"]["environment"])
build_function_dict = {"name":function_name, "environment":function_env, "build_config": build_config,
"service_config":service_config_dict}

# send request for function
request = functions_v2.CreateFunctionRequest(parent=parent, function=build_function_dict, function_id=data["function"]["function_name"])
operation = client.create_function(request=request)
response = operation.result()

print(response)