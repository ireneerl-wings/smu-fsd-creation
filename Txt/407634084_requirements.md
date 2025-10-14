# Extracted Requirements for SAP Delivery Optimization Enhancement

## System Requirements

### Functional Requirements

#### Core System Components
- **Satellite Application**: Delivery Optimizer system to enhance first mile distribution efficiency
- **SAP S/4HANA Integration**: Leverage data from delivery optimization satellite system for optimal delivery suggestions
- **Real-time Data Processing**: Integration of real-time data and advanced algorithms for delivery planning and execution
- **Multi-system Integration**: Integration with Blue Yonder, procurement systems, and form management

#### Key Business Processes
- **First Mile Delivery Optimization**: Focus on initial transportation stage with frequent and bulk shipments
- **Route Optimization**: Calculate most cost-effective and time-efficient delivery schedules
- **Resource Allocation**: Optimize vehicle, driver, and warehouse resource utilization
- **Constraint Management**: Handle product availability, order volume, and delivery windows

### Non-Functional Requirements

#### Performance Requirements
- **Average Load**: To be specified based on historical data
- **Peak Load**: To be specified with timing of peak demand
- **Real-time Processing**: System must process optimization requests in real-time
- **Scalability**: Handle multiple companies, shipping points, and destinations

#### Reliability Requirements
- **Data Consistency**: Maintain data integrity across integrated systems
- **Error Recovery**: Robust error handling for failed optimizations
- **Backup and Recovery**: Ensure data persistence and recovery capabilities

## Interfaces and Integrations

### External System Integrations
- **Blue Yonder Integration**: 
  - Host: 172.22.189.80 SID: manu
  - Table: SCPOUSR.UDT_RECSHIP_FINAL
  - Data retrieval based on NEEDSHIPDATE and shipping point parameters

- **SAP API Integrations**:
  - Promotion data retrieval (E0158)
  - Document generation APIs
  - Material master data access
  - Vendor master data access

- **Procurement API Integration** (A0024):
  - Kardus and PGMS data retrieval
  - Parameter-based data filtering

### Internal System Interfaces
- **Form Titipan Integration**: Access to t_form_titipan_hdr and t_form_titipan_dtl tables
- **Master Data Integration**: Access to location, material, vendor, and vehicle type masters
- **Authorization Integration**: User-based access control and data filtering

## Data Structures

### Input Data Structures

#### Delivery Optimization Input (t_input_delv)
```
- id (bigint, PK, auto-increment)
- source_data (varchar(150)) - Blue Yonder/Kardus/PGMS/Form Titipan
- req_pickup_date (date)
- company (varchar(50))
- region (varchar(50))
- ship_point (varchar(50))
- source_loc (varchar(50))
- source_plant (varchar(50))
- source_sloc (varchar(50))
- source_plant_manuf (varchar(50))
- ship_to_party (varchar(50))
- dest_type (varchar(50))
- dest_plant (varchar(50))
- dest_sloc (varchar(50))
- doc_type (varchar(50)) - SO/POSTO/PR
- doc_no (varchar(50))
- line_item (int)
- mid (varchar(50))
- mid_desc (varchar(250))
- ph2 (varchar(10))
- mg2 (varchar(10))
- qty (int)
- uom (varchar(10))
- qty_pallet (decimal)
- vol (decimal)
- weight (decimal)
- vol_total (decimal)
- weight_total (decimal)
- priority (int)
- highlevel_item (int)
- foc_flag (bool)
- reference (varchar(50))
- reference_2 (varchar(50))
- created_by (varchar(50))
- created_at (bigint)
```

#### Blue Yonder Data Structure (UDT_RECSHIP_FINAL)
```
- ITEM (material code)
- SOURCE (source location)
- DEST (destination location)
- SEQNUM (sequence number)
- QTY (quantity in sales unit)
- UDC_UOM (unit of measure)
- UDC_SHIPPING_POINT (shipping point)
- UDC_CUSTOMER_CODE (customer code)
- NEEDARRIVDATE (required arrival date)
- NEEDSHIPDATE (required ship date)
- AVAILTOSHIPDATE (available to ship date)
- SCHEDSHIPDATE (scheduled ship date)
- ITEM_PRIORITY (Yes/No priority flag)
```

### Output Data Structures

#### Delivery Optimization Header Output (t_output_delv_hdr)
```
- optimize_id (varchar(12), PK) - Format: Company(3)+YYMMDD+sequence(3)
- vehicle_id (int(4), PK)
- seq (int(4), PK)
- scm_req_date (date)
- company (varchar(50))
- ship_point (varchar(50))
- source_loc (varchar(50))
- source_plant (varchar(50))
- source_sloc (varchar(50))
- source_plant_manuf (varchar(50))
- dest_type (varchar(50))
- ship_to_party (varchar(50))
- dest_plant (varchar(50))
- dest_sloc (varchar(50))
- load_location (varchar(50))
- route_type (varchar(50))
- load_type (varchar(50))
- ship_type (varchar(50))
- carrier (varchar(50))
- liner (varchar(50))
- vessel (varchar(50))
- voy (varchar(50))
- port_of_loading (varchar(50))
- port_of_destination (varchar(50))
- vso (decimal)
- optimize_by (varchar(50))
- optimize_at (bigint)
- status (varchar(1)) - N/S/C (Not Generated/Scheduled/Generated)
- freight_order_source (varchar(10))
- freight_booking (varchar(10))
- freight_order_dest (varchar(10))
- schedule_by (varchar(50))
- schedule_at (bigint)
- generate_by (varchar(50))
- generate_at (bigint)
- note (varchar(250))
- changed_by (varchar(50))
- changed_at (bigint)
```

#### Delivery Optimization Detail Output (t_output_delv_dtl)
```
- optimize_id (varchar(12), PK)
- vehicle_id (int(4), PK)
- seq (int, PK)
- source_data (varchar(150), PK)
- line_item (int, PK)
- doc_type (varchar(50))
- doc_no (varchar(50))
- material (varchar(50))
- material_desc (varchar(250))
- ph2 (varchar(10))
- mg2 (varchar(10))
- qty (int)
- uom (varchar(10))
- qty_pallet (decimal)
- vol (decimal)
- weight (decimal)
- highlevel_item (int)
- foc_flag (bool)
- delivery (varchar(10))
- optimize_by (varchar(50))
- optimize_at (bigint)
- reference (varchar(50))
```

### Master Data Tables

#### Business Share (m_business_share)
```
- company (varchar(50), PK)
- vendor_code (varchar(10), PK)
- source_loc (varchar(50), PK)
- dest_type (varchar(50), PK)
- dest_loc (varchar(50), PK)
- ship_type (varchar(50), PK)
- route_type (varchar(50))
- business_share (decimal)
- share_cost (varchar(50))
- is_active (bool)
- created_by (varchar(50))
- created_at (bigint)
- updated_by (varchar(50))
- updated_at (bigint)
```

#### Container Availability (t_container_availability)
```
- vendor_code (varchar(10), PK)
- port_of_loading (varchar(50), PK)
- port_of_dest (varchar(50), PK)
- route_type (varchar(50))
- shipper_vendor (varchar(150), PK)
- vessel (varchar(150), PK)
- voy (varchar(150), PK)
- open_vessel (date)
- close_vessel (date)
- etd (date)
- eta (date)
- commit_20ft (int)
- commit_40ft_hc (int)
- commit_40ft (int)
- created_by (varchar(50))
- created_at (bigint)
- updated_by (varchar(50))
- updated_at (bigint)
```

#### Truck Availability (t_truck_availability)
```
- vendor_code (varchar(50), PK)
- availability_date (date, PK)
- ship_type (varchar(50), PK)
- company (varchar(50), PK)
- region (varchar(50), PK)
- available_qty (int)
- created_by (varchar(50))
- created_at (bigint)
- updated_by (varchar(50))
- updated_at (bigint)
```

## Process and Workflow Steps

### Delivery Optimization Planning Workflow

#### 1. Data Collection Phase
1. **Parameter Input**:
   - SCM Request Date (H+x days based on m_remarks)
   - Company Code (with user authorization check)
   - Source Shipping Point (default All, multi-select)
   - Destination Area (default All, multi-select)
   - Destination Location (default All, multi-select)

2. **Source Location Mapping**:
   - Map source plant and sloc from ZZXT_BY_LOCF_DPL and ZZXT_BY_LOCF_H
   - Map destination plant and sloc based on ship-to-party

3. **Data Retrieval**:
   - Get Blue Yonder data from UDT_RECSHIP_FINAL
   - Call SAP API for promotion data (E0158)
   - Call Procurement API for Kardus & PGMS data (A0024)
   - Retrieve Form Titipan data from local tables

#### 2. Data Processing Phase
1. **Data Consolidation**:
   - Insert all source data into t_input_delv table
   - Calculate quantities, volumes, and weights
   - Apply material master conversions (UOM, pallet calculations)
   - Set priorities and references

2. **Data Validation**:
   - Validate material master data
   - Check UOM conversions
   - Verify location mappings
   - Validate vendor and carrier data

#### 3. Optimization Phase
1. **Send to Python Engine**:
   - Transmit consolidated data to optimization engine
   - Apply business rules and constraints
   - Calculate optimal vehicle assignments and routes

2. **Receive Optimization Results**:
   - Insert results into t_output_delv_hdr and t_output_delv_dtl
   - Generate optimize_id with format: Company(3)+YYMMDD+sequence(3)
   - Set initial status to 'N' (Not Generated)

#### 4. Document Generation Workflow

##### Manual Generation
1. **User Selection**:
   - User selects vehicle IDs from Ready to Generate tab
   - System validates VSO thresholds against m_vso_threshold
   - Display confirmation dialog with optimization details

2. **SAP API Call**:
   - Send document generation request to SAP
   - Include all required parameters (materials, quantities, carriers, etc.)
   - Exclude materials with filled highlevel_item column

3. **Result Processing**:
   - Update t_output_delv_hdr with freight orders and booking numbers
   - Update t_output_delv_dtl with delivery numbers
   - Update t_form_titipan_hdr status to 'A' (Active)
   - Set status to 'C' (Generated)

##### Scheduled Generation
1. **Schedule Setup**:
   - User selects date and time for generation
   - System validates VSO thresholds
   - Set status to 'S' (Scheduled)

2. **Job Execution**:
   - Background job monitors scheduled items
   - Execute generation at specified time
   - Follow same API call and result processing as manual generation

### Master Data Management Workflows

#### Business Share Management
1. **Data Entry**:
   - Validate total active business share = 100% for manual share type
   - Support multiple vendors per route combination
   - Maintain audit trail (created_by, updated_by, timestamps)

2. **Validation Rules**:
   - Prevent duplicate primary key combinations
   - Ensure business share percentages are valid
   - Validate vendor and location master data

#### Container Vessel Availability
1. **Vendor Input**:
   - Vendors maintain availability through vendor portal
   - Input vessel schedules, capacity, and port information
   - System validates date ranges and capacity limits

2. **Capacity Tracking**:
   - Calculate available vs. used capacity
   - Track 20ft, 40ft, and 40ft HC containers separately
   - Update usage based on generated bookings

#### Truck Availability Management
1. **Time-based Restrictions**:
   - Implement threshold-based editing restrictions
   - Allow editing only for future dates or within threshold hours
   - Prevent modifications for past dates

2. **Capacity Management**:
   - Track availability by vendor, date, ship type, company, and region
   - Support multiple shipping types per vendor
   - Maintain real-time availability updates

## Test Scenarios and Validation Criteria

### Functional Test Scenarios

#### Delivery Optimization Planning Tests
1. **Valid Data Processing**:
   - Input: Valid SCM date, company, shipping points
   - Expected: Data retrieved from all sources and consolidated
   - Validation: Check t_input_delv table population

2. **Data Source Integration**:
   - Input: Blue Yonder, Kardus, PGMS, Form Titipan data
   - Expected: All sources integrated with proper mapping
   - Validation: Verify source_data field and calculations

3. **Optimization Engine Integration**:
   - Input: Consolidated input data
   - Expected: Optimization results in output tables
   - Validation: Check vehicle assignments and VSO calculations

#### Document Generation Tests
1. **Manual Generation Success**:
   - Input: Selected vehicle IDs with valid VSO
   - Expected: Documents generated in SAP
   - Validation: Status updated to 'C', freight orders populated

2. **VSO Threshold Validation**:
   - Input: Vehicle with VSO outside threshold range
   - Expected: Error message displayed
   - Validation: Generation blocked, status unchanged

3. **Scheduled Generation**:
   - Input: Future date/time for generation
   - Expected: Status set to 'S', job scheduled
   - Validation: Background job executes at specified time

#### Master Data Management Tests
1. **Business Share Validation**:
   - Input: Business shares not totaling 100%
   - Expected: Error message preventing save
   - Validation: Data not saved, user notified

2. **Container Availability Date Validation**:
   - Input: Open vessel date after close vessel date
   - Expected: Error message displayed
   - Validation: Data not saved, proper error handling

3. **Truck Availability Threshold**:
   - Input: Edit attempt after threshold time
   - Expected: Fields disabled or error shown
   - Validation: No unauthorized modifications allowed

### Error Handling and Exception Flows

#### Data Validation Errors
1. **Missing Required Fields**:
   - Error Type: Validation Error
   - Message: "Required field [field_name] cannot be empty"
   - Recovery: User must provide valid input

2. **Invalid Date Ranges**:
   - Error Type: Business Logic Error
   - Message: "Start date cannot be later than end date"
   - Recovery: User must correct date range

3. **Duplicate Records**:
   - Error Type: Data Integrity Error
   - Message: "Duplicate record found. Please check and modify your input"
   - Recovery: User must modify input to avoid duplication

#### Integration Errors
1. **SAP API Failure**:
   - Error Type: System Integration Error
   - Message: "Document generation failed. Please try again later"
   - Recovery: Retry mechanism, status remains unchanged

2. **Blue Yonder Connection Error**:
   - Error Type: External System Error
   - Message: "Unable to retrieve planning data. Please contact administrator"
   - Recovery: Manual retry, fallback to cached data if available

3. **Optimization Engine Error**:
   - Error Type: Processing Error
   - Message: "Optimization failed. Please check input data and try again"
   - Recovery: Data validation, manual optimization option

#### Business Rule Violations
1. **VSO Threshold Exceeded**:
   - Error Type: Business Rule Violation
   - Message: "VSO percentages do not meet the threshold requirements"
   - Recovery: Adjust optimization parameters or override with authorization

2. **Capacity Exceeded**:
   - Error Type: Capacity Constraint
   - Message: "Available capacity exceeded for selected vessel/truck"
   - Recovery: Select alternative vessel/truck or adjust quantities

## Security Requirements

### Authentication and Authorization
- **User Authentication**: Integration with corporate authentication system
- **Role-based Access Control**: Different access levels for different user types
- **Company-based Data Filtering**: Users can only access data for authorized companies
- **Shipping Point Authorization**: Access restricted based on user's shipping point assignments

### Data Security
- **Data Encryption**: Sensitive data encrypted in transit and at rest
- **Audit Trail**: Complete audit trail for all data modifications
- **Data Masking**: Sensitive information masked for unauthorized users
- **Backup and Recovery**: Regular backups with secure recovery procedures

### API Security
- **Secure Communication**: HTTPS/TLS for all API communications
- **API Authentication**: Token-based authentication for API access
- **Rate Limiting**: Prevent API abuse through rate limiting
- **Input Validation**: Comprehensive input validation to prevent injection attacks

## Performance, Scalability, and Reliability Requirements

### Performance Requirements
- **Response Time**: Optimization requests processed within 5 minutes
- **Concurrent Users**: Support minimum 100 concurrent users
- **Data Processing**: Handle up to 10,000 shipment records per optimization run
- **Report Generation**: Export functions complete within 2 minutes for standard datasets

### Scalability Requirements
- **Horizontal Scaling**: System architecture supports horizontal scaling
- **Database Performance**: Optimized database queries and indexing
- **Caching Strategy**: Implement caching for frequently accessed master data
- **Load Balancing**: Support for load balancing across multiple application servers

### Reliability Requirements
- **System Availability**: 99.5% uptime during business hours
- **Data Consistency**: ACID compliance for all database transactions
- **Error Recovery**: Automatic recovery from transient errors
- **Monitoring**: Comprehensive monitoring and alerting for system health

## User Interaction Requirements

### User Interface Requirements
- **Responsive Design**: Support for desktop and tablet devices
- **Intuitive Navigation**: Clear menu structure and breadcrumb navigation
- **Data Visualization**: Charts and graphs for optimization results
- **Export Capabilities**: Multiple export formats (Excel, CSV, PDF)

### Accessibility Requirements
- **WCAG Compliance**: Meet WCAG 2.1 AA accessibility standards
- **Keyboard Navigation**: Full keyboard navigation support
- **Screen Reader Support**: Compatible with common screen readers
- **Color Contrast**: Adequate color contrast for visually impaired users

### User Experience Requirements
- **Consistent UI**: Consistent look and feel across all modules
- **Error Messages**: Clear, actionable error messages
- **Help Documentation**: Context-sensitive help and user guides
- **Training Materials**: Comprehensive training materials and tutorials

## Additional Constraints and Assumptions

### Technical Constraints
- **SAP S/4HANA Version**: Compatible with current SAP S/4HANA version
- **Database Platform**: PostgreSQL for satellite application data
- **Integration Platform**: RESTful APIs for system integration
- **Browser Support**: Support for modern browsers (Chrome, Firefox, Safari, Edge)

### Business Constraints
- **Regulatory Compliance**: Comply with local transportation and logistics regulations
- **Business Hours**: System maintenance windows outside business hours
- **Data Retention**: Maintain historical data for minimum 7 years
- **Vendor Agreements**: Integration subject to vendor API availability and terms

### Assumptions
- **Network Connectivity**: Reliable network connectivity between systems
- **User Training**: Users will receive adequate training before system deployment
- **Data Quality**: Source systems provide accurate and timely data
- **Change Management**: Proper change management processes in place for system updates

This comprehensive requirements extraction covers all aspects of the SAP Delivery Optimization Enhancement as described in the functional specification document, providing a complete foundation for system development and implementation.