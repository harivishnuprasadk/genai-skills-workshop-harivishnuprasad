#Create model with connection
CREATE OR REPLACE MODEL `my_data_faq.Embeddings`
REMOTE WITH CONNECTION `us.embedding_conn`
OPTIONS (ENDPOINT = 'text-embedding-005');

#Load data
LOAD DATA OVERWRITE my_data_faq.faq
(
    question STRING,
    answer STRING
)
FROM FILES (
    format = 'CSV',
    uris = ['gs://labs.roitraining.com/aurora-bay-faqs/aurora-bay-faqs.csv']
);
 
 #create embeddings
CREATE OR REPLACE TABLE `my_data_faq.aurora_bay_faq_embedded` AS 
SELECT * 
FROM ML.GENERATE_EMBEDDING(
    MODEL `my_data_faq.Embeddings`,
    (SELECT 
        question,
        answer,
        CONCAT('Question: ', question, ' Answer: ', answer) AS content 
     FROM `my_data_faq.faq`
     WHERE question != 'question'  -- Exclude header row
     AND answer != 'answer'        -- Exclude header row
     AND question IS NOT NULL      -- Exclude null values
     AND answer IS NOT NULL)       -- Exclude null values
);

