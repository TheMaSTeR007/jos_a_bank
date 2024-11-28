# Define your item pipelines here
import logging
from jos_a_bank.items import JosABankItem
from jos_a_bank import db_config
import colorlog

# Configure the logging format and set up the logger
handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    fmt="%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)
handler.setFormatter(formatter)

# Set up the logger
logger = logging.getLogger('storeLocatorPipelineLogger')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class JosABankPipeline:
    # Called when the spider is opened
    def open_spider(self, spider):
        # Set the database table name based on the spider's name and the delivery date
        db_data_table = f"{spider.name}_{db_config.delivery_date}"

        # SQL query to create the table if it doesn't already exist
        create_table = f"""CREATE TABLE `{db_data_table}` (
                            `store_no` VARCHAR(50),
                            `name` VARCHAR(500),
                            `latitude` VARCHAR(500),
                            `longitude` VARCHAR(500),
                            `street` VARCHAR(500),
                            `city` VARCHAR(100),
                            `state` VARCHAR(500),
                            `zip_code` VARCHAR(500),
                            `county` VARCHAR(500),
                            `phone` VARCHAR(500),
                            `open_hours` VARCHAR(500),
                            `url` VARCHAR(500),
                            `provider` VARCHAR(500),
                            `category` VARCHAR(500),
                            `updated_date` VARCHAR(500),
                            `country` VARCHAR(500),
                            `status` VARCHAR(500),
                            `direction_url` VARCHAR(500)
                            );"""
        # CONSTRAINT unique_city_store UNIQUE (`city`, `store_no`)
        # `store_no` VARCHAR(500) UNIQUE,

        try:
            # Execute the table creation query
            spider.cursor.execute(create_table)
            logger.info(f'{db_data_table} table created.')
        except Exception as e:
            # Log any errors encountered during table creation
            logger.warning(f"Error creating table: {e}")

    # Called for each item scraped
    def process_item(self, item, spider):
        # Set the database table name based on the spider's name and the delivery date
        db_data_table = f"{spider.name}_{db_config.delivery_date}"

        # item.pop('index_id')
        # spider.collection.insert_one(dict(item))
        # Check if the item is an instance of StorelocatorItem
        if isinstance(item, JosABankItem):
            # index_id = item['index_id']
            copy_item = item.copy()  # Make a copy of the item to avoid mutating the original
            # copy_item.pop('index_id')

            # Prepare the SQL query for inserting data
            cols = ', '.join(copy_item.keys())  # Join the column names
            values = tuple(copy_item.values())  # Extract values as a tuple
            placeholders = ', '.join(['%s'] * len(copy_item))  # Create placeholders for the query

            # Construct the insert query
            insert_query = f"INSERT INTO `{db_data_table}` ({cols}) VALUES ({placeholders});"

            try:
                # Insert data into the database
                logger.info(f'Inserting data into {db_data_table}.')
                spider.cursor.execute(query=insert_query, args=values)
                logger.info('Data inserted successfully.')
                # update_q = f'''UPDATE {spider.input_table} SET status = 'done' WHERE index_id = {index_id}'''
                # spider.cursor.execute(update_q)
                # logger.info('Status updated successfully.')
            except Exception as e:
                # Log any errors encountered during insertion
                logger.error(f'Error inserting data into {db_data_table}: {e}')

        # Return the item for further processing in the pipeline
        return item
