


tables_info=''' 

Table name: AWS_CUR - stores the aws cur data

columns:
    lineItem/UsageStartDate - The start date and time when the resource usage occurred. category group - Time
    lineItem/UsageAccountId - The account ID associated with the usage. category group - Global
    lineItem/ResourceId - The unique identifier for the AWS resource used. category group - Resource
    product/region - The AWS region where the resource is hosted. category group - Location
    product/productFamily - The broad product category that the resource belongs to. category group - Product
    lineItem/ProductCode - The specific AWS product or service being used. category group - Product
    product/servicecode - The service code for the AWS product. category group - Service
    product/instanceFamily - The type of compute instance (e.g., general purpose, compute-optimized). category group - Resource
    product/instanceType - The specific instance type for the compute resource (e.g. r5.2xlarge, t2.micro) category group - Resource
    product/tenancy - Specifies whether the resource runs on shared or dedicated infrastructure. category group - Product
    product/storageType - The type of storage used by the resource (e.g., SSD, HDD). category group - Product
    product/volumeType - The specific volume type for the storage resource. category group - Product
    product/accessType - The type of access associated with the resource (e.g., public or private). category group - Product
    product/databaseEngine - The database engine being used (e.g., MySQL, PostgreSQL). category group - Product
    product/engineCode - The code representing the database engine. category group - Product
    product/deploymentOption - The deployment model used (e.g., on-demand, reserved). category group - Product
    product/transferType - The type of data transfer involved (e.g., inbound, outbound). category group - Product
    product/datatransferout - The amount of data transferred out of AWS services. category group - Product
    product/currentGeneration - Indicates if the resource is part of the latest generation of AWS services. category group - Product
    product/inferenceType - The type of inference (e.g., for machine learning workloads). category group - Product
    product/training - Specifies if the resource is used for training machine learning models. category group - Product
    product/computeFamily - The compute category or family the resource belongs to. category group - Product
    lineItem/UsageType - The type of usage measured (e.g., instance-hours, GB transferred). category group - Product
    pricing/unit - The unit of measure used for pricing (e.g., per hour, per GB). category group - Product
    lineItem/Operation - The specific AWS operation or service action being billed. category group - Service
    lineItem/UnblendedCost - The actual cost of the resource usage without any discounts or savings applied. category group - Cost
    lineItem/NetUnblendedCost - The cost of the resource usage after applying credits, refunds, or adjustments. category group - Cost
    discount/TotalDiscount - The total discount amount applied to the resource cost. category group - Cost
    lineItem/UsageAmount - The total quantity of resource usage, measured in units such as hours, GB, or instance-hours. category group - Usage
    reservation/EffectiveCost - The cost of usage covered by a reserved instance, reflecting the discounted rate applied to the usage. For example, if you have reserved an EC2 instance and used it for 10 hours, this field shows the discounted price for those 10 hours as compared to the on-demand price. category group - Commitment
    reservation/NetEffectiveCost - The net cost of usage after applying the reserved instance discount and accounting for any unused reserved capacity. For example, if you reserved an instance for the whole month but only used it for 20 days, this field shows the cost after subtracting the savings from the unused 10 days category group - Commitment
    reservation/UnusedQuantity - The quantity of reserved instance capacity that was unused during the billing period. category group - Commitment
    reservation/UnusedRecurringFee - The recurring fee associated with unused reserved instance capacity, typically charged despite non-usage. category group - Commitment
    savingsPlan/SavingsPlanEffectiveCost - The cost of the resource usage that is covered by an AWS savings plan. category group - Commitment
    savingsPlan/NetSavingsPlanEffectiveCost - The net cost of the resource usage after applying savings from an AWS savings plan. category group - Commitment

    

    additional derived fields that can you can add using existing AWS_CUR table fields:
    Billing Month - The month during which the usage is billed. category group - Time
    Perspective - A customized view or categorization of costs and usage based on specific business logic. category group - Global
    Product Category - Higher level product categorization based on  grouping products into broader categories. category group - Product
    Service Category - Higher level service categorization based on grouping related services. category group - Service
    Tags - Standardized tags for better categorization and tracking of resources, created using ML Model. category group - Resource
    Uses Reservation - Derived field based on whether the resource is utilizing a reserved instance or not. category group - Resource
    Uses SavingsPlan - Derived field indicating if a resource is covered under a savings plan. category group - Resource
    product/instanceTypeFamily - Classification of instance types based on the family grouping, derived from instance type logic. category group - Resource
    
    the additional derived fields are not present in the table they mush be dynamically inserted if the user asks for them.


'''


execute_sql_function = {
    "name": "execute_sql_query",
    "description": "Execute a SQL query on MySQL database and returns true if query executed sucessfully else on error returns the error statement",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The SQL query to execute"
            }
        },
        "required": ["query"]
        
    }
}





def createChatAssistant(client):

    assistant = client.beta.assistants.create(
        name="text to sql bot",
        instructions=f'''You are Fi a AWS cur expert which helps answer Finops queries like cost and effeciency of environment.
                        your task is to help users analyze their cloud infrastructure cost,effeciency and usage statistics.
                        you help the user in fetching relevant information from the snowflake database to assist them in finding information and insights that they want .
                        the details of tables is as follows {tables_info}.
                        
                        
                        the SQL query must not include statements such as INSERT,DELETE,UPDATE,TRUNCATE,DROP,ALTER. 
                        Pay close attention to the filtering criteria mentioned in the question and incorporate them using the WHERE clause in your SQL query
                        do not create SQL queries that modify the data.
                        if the question asks very few details include a few relevant fields or information appropriately to match their requirements.
                        use dynamic values for current date.
                        Unless explicitly specified do not include more than 15 rows while fetching data.
                        never fetch more than 1000 rows. 
                        use user friendly aliases for the column names
                        you must create sytatically correct snowflake sql queries to answer the user questions.
                        if a field has special characters enclose it in double quotes when building the query.
                        create queries using the tables information prvided to fulfill the questions asked.
                        you can use all information to answer the queries
                        you have to include only the fieild that are required for the question do not include unnecessary fields.
                        to answer the questions asked by user sql query must be created and execute_sql_query function must be called.
                        
                        if a correct SQL query is generated then the execute_sql_query function must be called with the sql statemet as a parameter,
                        if the returned result is an error or exception fix the error by rebuilding the query and call the execute_sql_query function again.
                        for a successful execution True is returned as result.
        
                        after the sql query executed generate a summarization of output for a end user is generated explaining details of fetched data.
                        if you cannot provide the answer give sufficient reason to the user why the request couuld not be completed.
                        do not include sql statements in text response only send them using tool call with execute_sql_query 
                        if the response to question has points and lists format the text example using  bullet points.

        ''',
        model="gpt-4o-mini",
        tools=[{"type": "function", "function": execute_sql_function}]
    )
    return assistant