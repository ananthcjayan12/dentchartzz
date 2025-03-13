import os
import django
import sys
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

try:
    # Get the cursor
    cursor = connection.cursor()
    
    # Create the app_paymentitem table
    cursor.execute("""
    CREATE TABLE app_paymentitem (
        id bigint NOT NULL,
        description character varying(255) NOT NULL,
        amount numeric(10,2) NOT NULL,
        payment_id bigint NOT NULL,
        treatment_id bigint NULL,
        CONSTRAINT app_paymentitem_pkey PRIMARY KEY (id),
        CONSTRAINT app_paymentitem_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES app_payment(id) ON DELETE CASCADE,
        CONSTRAINT app_paymentitem_treatment_id_fkey FOREIGN KEY (treatment_id) REFERENCES app_treatment(id) ON DELETE SET NULL
    );
    
    -- Create sequence for id
    CREATE SEQUENCE app_paymentitem_id_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;
        
    -- Set the sequence as default for id
    ALTER TABLE ONLY app_paymentitem ALTER COLUMN id SET DEFAULT nextval('app_paymentitem_id_seq'::regclass);
    """)
    
    # Commit the transaction
    connection.commit()
    
    print("Successfully created app_paymentitem table")
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1) 