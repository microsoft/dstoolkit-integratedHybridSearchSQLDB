#file to create a skillset for Azure AI Search
#with Azure OpenAi Embedding
#with TextSplit
from azure.search.documents.indexes.models import (  
SplitSkill, InputFieldMappingEntry, OutputFieldMappingEntry,AzureOpenAIEmbeddingSkill, SearchIndexerIndexProjections, SearchIndexerIndexProjectionSelector,
SearchIndexerSkillset
)
from azure.search.documents.indexes import SearchIndexerClient
from azure.core.credentials import AzureKeyCredential
import openai 
import os

openai_uri = os.environ.get("OPENAI_URI")
openai_deployment = os.environ.get("OPENAI_DEPLOYMENT")
openai.api_key = os.environ.get("OPENAI_API_KEY")

index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME")
service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
aisearch_key = os.environ.get("AZURE_SEARCH_KEY")

def createSkillset():
    skillset_name = index_name + "-skillset"

    #Splitskill to chunk text
    split_skill = SplitSkill(
        description="Split skill to chunk documents",
        text_split_mode="pages",
        context="/document",
        maximum_page_length=300,
        page_overlap_length=20,
        inputs=[
            InputFieldMappingEntry(name="text", source="/document/Description")
        ],
        outputs=[
            OutputFieldMappingEntry(name="textItems", target_name="pages")
        ]    
    )

    #Embedding skill to vectorize text
    embedding_skill = AzureOpenAIEmbeddingSkill(
        description="Skill to generate embeddings via Azure OpenAI",  
        context="/document/pages/*", 
        resource_uri = openai_uri,
        deployment_id=openai_deployment,
        api_key=openai.api_key,
        inputs=[
            InputFieldMappingEntry(name="text", source="/document/pages/*")
        ],
        outputs=[
            OutputFieldMappingEntry(name="embedding", target_name="vector")
        ]
    )
    #index projections of db rows
    #
    index_projections = SearchIndexerIndexProjections(
        selectors=[
            SearchIndexerIndexProjectionSelector(
                target_index_name=index_name,
                parent_key_field_name="db_table_id",
                source_context="/document/pages/*",
                mappings=[
                    InputFieldMappingEntry(name="chunk", source="/document/pages/*"),
                    InputFieldMappingEntry(name="vector", source="/document/pages/*/vector"),
                    InputFieldMappingEntry(name="db_table_year", source="/document/Year"),
                    InputFieldMappingEntry(name="db_table_discipline", source="/document/Discipline"),
                    InputFieldMappingEntry(name="db_table_winner", source="/document/Winner"),
                    InputFieldMappingEntry(name="db_table_description", source="/document/Description")
                    
                ]
            )
        ]
    )

    skillset = SearchIndexerSkillset(
        name=skillset_name,
        description="Skillset for Azure AI Search with Azure OpenAI Embedding",
        skills=[
            split_skill,
            embedding_skill
        ],
        index_projections=index_projections
    )
    #create Skillset with split and embedding skills
    c = SearchIndexerClient(service_endpoint, AzureKeyCredential(aisearch_key))  
    c.create_or_update_skillset(skillset)  
    print(f"{skillset.name} created")  
    