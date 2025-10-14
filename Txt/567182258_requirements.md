# SAP Functional Specification Document - Requirements Analysis

## System Requirements

### Functional Requirements

#### **1. Reserved Space Threshold Enhancement**
- **Requirement**: Add new column "unit" to existing Reserved Space Threshold functionality
- **Data Structure**: 
  - Table: `m_reserved_threshold`
  - New field: `unit` (varchar(5), value restriction: %m3)
- **UI Requirement**: Display unit field as dropdown from `m_remarks` where group_code = 'unit_titipan'

#### **2. Business Share Trucking - Export (New Menu)**
- **Purpose**: Maintain business share for trucking vendors
- **Data Source**: Table `m_busshare_truck_export`
- **Key Features**:
  - Add, Edit, Delete functionality
  - Upload/Export capabilities
  - Validation for business share totals (must equal 100%)
  - Duplicate prevention for trucking vendors

#### **3. Business Share Liner - Export (New Menu)**
- **Purpose**: Maintain business share for liner vendors  
- **Data Source**: Table `m_busshare_liner_export`
- **Key Features**:
  - Add, Edit, Delete functionality
  - Upload/Export capabilities
  - Validation for business share totals (must equal 100%)
  - Duplicate prevention for liner combinations

#### **4. Vessel Schedule - Export (New Menu)**
- **Purpose**: Maintain vessel schedules for export operations
- **Data Source**: Table `t_vessel_schedule_export`
- **Key Features**:
  - Add, Edit, Delete schedules
  - Upload/Export capabilities
  - Date validation (past dates restrictions)
  - Schedule conflict prevention

#### **5. Container Type Master (New Menu)**
- **Purpose**: Maintain container types related to MTO
- **Data Source**: Table `m_container_type`
- **Key Features**:
  - Add/Delete container types
  - Upload/Export capabilities
  - Container type validation (20/40 ft)

#### **6. Optimization Planning - Export (New Menu)**
- **Purpose**: Optimize demand from Blue Yonder and generate FB groups/vehicles
- **Key Features**:
  - Data integration with Blue Yonder system
  - SAP API integration for SO information
  - Material management (FOC Declare/Non-Declare)
  - Optimization engine integration

#### **7. Optimization Result - Export (New Menu)**
- **Purpose**: Access optimization results per company and market type
- **Key Features**:
  - Document generation to SAP
  - Schedule management
  - Status tracking (Ready to Generate/Scheduled)
  - Summary reporting

#### **8. Optimization Report - Export (New Menu)**
- **Purpose**: Monitor delivery optimization results
- **Key Features**:
  - Comprehensive reporting
  - Data filtering by market type, company, date ranges
  - Export capabilities

### Non-Functional Requirements

#### **Performance Requirements**
- System must handle 200+ data entries per table
- Pagination support (10/20/50/100 items per page)
- Real-time data validation
- Efficient data processing for optimization engine

#### **Scalability Requirements**
- Support for multiple companies and shipping points
- User authorization-based data filtering
- Concurrent user access support

#### **Reliability Requirements**
- Data integrity validation
- Transaction rollback capabilities
- Error handling and recovery mechanisms

## Data Structures

### **Input Data Structures**

#### **Business Share Trucking Table** (`m_busshare_truck_export`)
```sql
- id (bigserial - PK)
- source_loc (varchar(50) - PK)
- company (varchar(50))
- port_of_loading (varchar(50) - PK)
- ship_type (varchar(50) - PK)
- vendor (varchar(10) - PK)
- share_cost (varchar(50))
- business_share (float8)
- is_active (bool)
- created_by (varchar(50))
- created_at (bigint)
- updated_by (varchar(50))
- updated_at (bigint)
```

#### **Business Share Liner Table** (`m_busshare_liner_export`)
```sql
- id (bigserial - PK)
- port_of_loading (varchar(50) - PK)
- port_of_destination (varchar(50) - PK)
- ship_type (varchar(50) - PK)
- liner (varchar(50) - PK)
- execution_liner (varchar(50) - PK)
- share_cost (varchar(50))
- business_share (float8)
- is_active (bool)
- created_by (varchar(50))
- created_at (bigint)
- updated_by (varchar(50))
- updated_at (bigint)
```

#### **Vessel Schedule Table** (`t_vessel_schedule_export`)
```sql
- id (bigserial - PK)
- port_of_loading (varchar(50) - PK)
- port_of_destination (varchar(50) - PK)
- liner (varchar(10) - PK)
- execution_liner (varchar(10) - PK)
- vessel (varchar(50) - PK)
- voy (varchar(50) - PK)
- open_vessel (date - PK)
- close_vessel (date - PK)
- cut_off_doc (date)
- etd (date)
- eta (date)
- actual_open_vessel (date)
- actual_close_vessel (date)
- created_by (varchar(50))
- created_at (bigint)
- updated_by (varchar(50))
- updated_at (bigint)
```

### **Output Data Structures**

#### **Optimization Header Output** (`t_output_delv_hdr_ex`)
```sql
- optimize_id (varchar(12) - PK)
- vehicle_id (int(4) - PK)
- fb_group (int(4))
- scm_req_date (date)
- company (varchar(50))
- ship_point (varchar(50))
- source_loc (varchar(50))
- [... additional fields for shipping details]
- status (varchar(1)) // C=Generated, S=Scheduled, N=Not Generated
- created_by (varchar(50))
- created_at (bigint)
```

#### **Optimization Detail Output** (`t_output_delv_dtl_ex`)
```sql
- optimize_id (varchar(12) - PK)
- vehicle_id (int(4) - PK)
- source_data (varchar(150) - PK)
- doc_type (varchar(50))
- doc_no (varchar(50))
- line_item (int - PK)
- material (varchar(50))
- material_desc (varchar(250))
- qty (int)
- uom (varchar(10))
- vol (decimal)
- weight (decimal)
- delivery (varchar(10))
- created_by (varchar(50))
- created_at (bigint)
```

## Interfaces & Integrations

### **External System Integrations**

#### **1. Blue Yonder Integration**
- **Host**: 172.22.189.80
- **Database**: SCPOUSR.UDT_RECSHIP_FINAL
- **Purpose**: Retrieve demand data for optimization
- **Data Flow**: Blue Yonder → Delivery Optimization System

#### **2. SAP API Integration**
- **API Endpoint**: E0400 (SO Information)
- **Purpose**: Retrieve Sales Order details, container information
- **Input**: SO Numbers array
- **Output**: Header, Detail, Container data structures

#### **3. Python Optimization Engine**
- **Object ID**: E0423
- **Purpose**: Process optimization algorithms
- **Integration Point**: Called when user clicks "Optimize" button

### **Internal System Integrations**

#### **Reference Tables**
- `general.m_location` - Location master data
- `general.m_company_code` - Company information
- `general.m_shipping_point` - Shipping point data
- `mdg.m_bp_general_view` - Business partner information
- `general.m_vehicle_type` - Equipment/vehicle types
- `general.m_material` - Material master data

## Process Workflows

### **1. Business Share Management Workflow**
1. **Data Entry**: User selects source location, loading port, shipping type
2. **Vendor Selection**: Choose trucking/liner vendors with business share percentages
3. **Validation**: System validates total business share = 100%
4. **Save**: Data stored in respective tables
5. **Audit Trail**: Created/updated timestamps and user tracking

### **2. Optimization Planning Workflow**
1. **Parameter Setting**: User sets market type, SCM date, company, shipping points
2. **Data Retrieval**: System fetches data from Blue Yonder and SAP
3. **Material Management**: Handle FOC materials (Declare/Non-Declare)
4. **Optimization**: Send data to Python engine for processing
5. **Result Storage**: Store optimization results in output tables

### **3. Document Generation Workflow**
1. **Result Review**: User reviews optimization results
2. **Validation**: Check VSO thresholds and container requirements
3. **SAP Integration**: Generate documents in SAP system
4. **Status Update**: Update records with generated document numbers
5. **Scheduling**: Option to schedule generation for future execution

## Security Requirements

### **Authentication & Authorization**
- User-based access control for company codes and shipping points
- Role-based permissions for different menu functions
- Audit trail for all data modifications

### **Data Security**
- Input validation for all user entries
- SQL injection prevention
- Data encryption for sensitive information

### **Compliance Requirements**
- SOX compliance for financial data
- Audit logging for all transactions
- Data retention policies

## Validation & Error Handling

### **Business Rule Validations**

#### **Business Share Validation**
- Total active business share must equal 100%
- No duplicate vendor combinations allowed
- Status-based validation (active/inactive)

#### **Date Validations**
- Open vessel cannot be greater than cut-off date
- Close vessel cannot be greater than ETD
- ETD cannot be greater than ETA
- Past date restrictions for planned schedules

#### **VSO Threshold Validation**
- Check against `m_vso_threshold` table
- Bypass validation for LCL containers
- Skip non-compliant vehicles with error notification

### **Error Messages**
- "Total active business share must equal 100%"
- "Duplicate liner is not allowed"
- "Open Vessel cannot be more than Cut Off Doc!"
- "Some schedules are past their open vessel date and cannot be deleted"

## Performance & Scalability

### **Performance Requirements**
- Page load time < 3 seconds
- Optimization processing time < 5 minutes
- Real-time validation response < 1 second

### **Scalability Considerations**
- Support for 200+ data entries per table
- Concurrent user sessions
- Batch processing capabilities for large datasets

### **Reliability Requirements**
- 99.9% system availability
- Automatic failover capabilities
- Data backup and recovery procedures

## User Interface Requirements

### **Navigation Structure**
- Left sidebar menu with module organization
- Breadcrumb navigation
- Search and filter capabilities
- Pagination controls

### **Form Controls**
- Dropdown menus with autocomplete
- Date picker controls
- Radio buttons for single selection
- Checkboxes for multiple selection
- Modal dialogs for confirmations

### **Accessibility Requirements**
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance
- Responsive design for different screen sizes

## Test Scenarios

### **Functional Testing**
1. **Business Share Management**: Test add/edit/delete operations with validation
2. **Optimization Process**: End-to-end testing from planning to document generation
3. **Integration Testing**: Verify Blue Yonder and SAP API connections
4. **User Authorization**: Test role-based access controls

### **Performance Testing**
1. **Load Testing**: Simulate multiple concurrent users
2. **Stress Testing**: Test system limits with large datasets
3. **Integration Performance**: Test external API response times

### **Security Testing**
1. **Authentication Testing**: Verify user login and session management
2. **Authorization Testing**: Test role-based access restrictions
3. **Data Validation Testing**: Test input sanitization and validation

This comprehensive requirements analysis covers all functional and non-functional aspects of the SAP Delivery Optimization Enhancement system, providing a complete foundation for development and implementation.