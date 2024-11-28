from datetime import datetime

db_host = 'localhost'
db_user = 'root'
db_password = 'actowiz'
db_port = 3306

delivery_date = datetime.today().strftime("%d-%m-%Y")
db_name = 'storeLocator'

# table query
# CREATE TABLE IF NOT EXISTS {db_config.db_data_table} (
#             `index_id` INT AUTO_INCREMENT PRIMARY KEY,
#             `store_no` VARCHAR(500),
#             `name` VARCHAR(500),
#             `latitude` VARCHAR(500),
#             `longitude` VARCHAR(500),
#             `street` VARCHAR(500),
#             `city` VARCHAR(500),
#             `state` VARCHAR(500),
#             `zip_code` VARCHAR(500),
#             `county` VARCHAR(500),
#             `phone` VARCHAR(500),
#             `open_hours` VARCHAR(500),
#             `url` VARCHAR(500),
#             `provider` VARCHAR(500),
#             `category` VARCHAR(500),
#             `updated_date` VARCHAR(500),
#             `country` VARCHAR(500),
#             `status` VARCHAR(500),
#             `direction_url` VARCHAR(500)
#         );
