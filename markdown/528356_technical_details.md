# Technical Implementation Details
## Microsoft Teams Room Upgrade for ACC-DTA

### Equipment Specifications

#### Microsoft Teams Room Systems
We recommend implementing Microsoft-certified Teams Room systems for each location. For this project, we propose using the following configuration:

1. **Compute Platform**: Lenovo ThinkSmart Core or equivalent
   - Intel Core i5 processor (or better)
   - 8GB RAM minimum
   - 128GB SSD storage
   - Windows 10 IoT Enterprise
   - Microsoft Teams Rooms app

2. **Cameras**:
   - **Executive Director's Office**: Logitech Rally Camera or equivalent
     - 1080p/60fps capability
     - 15x optical zoom
     - 90° field of view
     - Pan/tilt/zoom functionality
     - USB 3.0 connectivity
     - Remote control capable

   - **Executive Conference Room**: Logitech Rally Camera or equivalent
     - 1080p/60fps capability
     - 15x optical zoom
     - 90° field of view
     - Pan/tilt/zoom functionality
     - USB 3.0 connectivity

   - **Basement Training Room**: 3x PTZ Optics 12X-SDI-GY-G2 (equivalent replacement)
     - 1080p/60fps capability
     - 12x optical zoom
     - 72.5° field of view
     - Pan/tilt/zoom functionality
     - SDI and USB 3.0 outputs

3. **Auxiliary Equipment**:
   - USB extenders (where required)
   - HDMI-to-USB capture devices (if needed)
   - Control system integration modules
   - Cable management solutions

### System Integration Details

#### 1. Executive Director's Office

**Current Equipment to Remain:**
- Dell WD19 Docking Station
- Two Cisco Table Microphones
- Display monitor
- Crestron touch panel

**Integration Approach:**
1. Remove Cisco SX80 codec and Precision 60 camera
2. Install Microsoft Teams Room compute system
3. Install new PTZ camera on wall mount (same location as existing)
4. Integrate with existing microphones via USB audio interface
5. Reprogram touch panel for Teams control
6. Configure system for one-touch meeting join
7. Program room control for lighting and display management

**Signal Flow:**
- Camera → USB → Teams Room System
- Microphones → USB Audio Interface → Teams Room System
- Teams Room System → HDMI → Display
- Control System ← Network → Teams Room System

#### 2. Executive Conference Room

**Current Equipment to Remain:**
- Four Sharp TVs (2x PN-LE901, 2x LE-701)
- Crestron DM MD8X8 Digital Media Switcher
- Crestron DM-RMC-4K-SCALER-C RECEIVER
- Crestron DM-TX-4K-302-C DigitalMedia Transmitter
- Crestron CP3N
- BIAMP TESIRAFORTE AVB VT
- Crestron AMP-2210HT power amplifier
- Six ceiling speakers (Crestron SAROS_IC6T)
- Three beamtracking ceiling microphones (Biamp Tesira TCM-1EX)
- Crestron DM-MD-8X8 video matrix

**Integration Approach:**
1. Remove Cisco SX80 codec and Precision 60 camera
2. Install Microsoft Teams Room compute system
3. Install new PTZ camera on wall mount (same location as existing)
4. Integrate with Biamp audio system via USB audio connection
5. Reprogram Crestron control system for display management
6. Configure system for content sharing to multiple displays
7. Update touch panel interface for intuitive operation

**Signal Flow:**
- Camera → USB → Teams Room System
- Biamp Audio System → USB → Teams Room System
- Teams Room System → HDMI → Crestron DM Matrix → Displays
- Content Sharing Devices → HDMI → Crestron DM Matrix
- Control System ← Network → Teams Room System

#### 3. Basement Training Room

**Current Equipment to Remain:**
- Five displays (1x NEC 75" LCD TV V754Q, 4x NEC 98" V984Q)
- Eleven ELECTROVOICE C6.2 in-ceiling speakers
- Six AUDIX M3W ceiling microphones
- Crestron touchpanel TS-1070-W-S

**Integration Approach:**
1. Remove Cisco SX80 codec
2. Replace three PTZ Optics cameras with Teams-compatible equivalents
3. Install Microsoft Teams Room compute system
4. Integrate with existing audio system
5. Configure camera switching for Teams meetings
6. Reprogram touch panel for camera selection and Teams control
7. Set up content routing to all displays

**Signal Flow:**
- Three PTZ Cameras → USB → Teams Room System
- Audio System → USB → Teams Room System
- Teams Room System → HDMI → Video Distribution System → Displays
- Control System ← Network → Teams Room System, Cameras, and Audio System

### Programming Requirements

#### Touch Panel Reprogramming

The existing touch panels will require new user interfaces and programming to:

1. **Remove VTC Functions:**
   - Eliminate Cisco VTC dial pad and directory
   - Remove codec control elements
   - Delete unused camera preset buttons

2. **Add Teams Controls:**
   - One-touch meeting join functionality
   - Camera control interface for pan/tilt/zoom
   - Camera preset selection (for multiple cameras)
   - Audio mute/unmute controls
   - Content sharing controls

3. **Maintain Existing Functions:**
   - Source selection for local presentations
   - Display power and input selection
   - Audio level control
   - Lighting control (if applicable)

4. **Example Interface Screens:**
   - Welcome/Home screen with system on/off
   - Meeting selection (Teams or local presentation)
   - Source selection screen for HDMI and wireless inputs
   - Camera control screen
   - Settings and help screens

#### Control System Programming

The Crestron control systems will be programmed to:

1. **Manage Signal Routing:**
   - Route MTR output to appropriate displays
   - Route content sharing devices to displays
   - Switch camera inputs for multi-camera setups

2. **Provide Device Control:**
   - Power on/off displays
   - Control PTZ camera movements
   - Adjust audio levels
   - Manage lighting and shades (if applicable)

3. **Enable System Monitoring:**
   - Device online/offline status
   - System temperature monitoring
   - Error logging and reporting

### Installation Process

#### Pre-Installation Preparations:
1. Bench test all new equipment
2. Develop and test control system programming
3. Pre-configure Microsoft Teams Room systems
4. Prepare cable assemblies and mounting hardware

#### Installation Sequence:
1. **Documentation of Existing Systems:**
   - Take detailed photos of all connections
   - Document cable labels and terminations
   - Verify equipment inventory

2. **Equipment Removal:**
   - Carefully disconnect and remove Cisco codecs
   - Remove Cisco cameras while preserving mounting locations
   - Label and organize all cables for potential reuse

3. **New Equipment Installation:**
   - Mount new cameras in same locations as existing
   - Install Microsoft Teams Room systems
   - Connect all video, audio, USB, and control cables
   - Implement cable management

4. **Integration and Testing:**
   - Connect to network
   - Configure Teams Room systems
   - Test camera functionality
   - Verify audio pickup and reproduction
   - Test content sharing capabilities
   - Validate control system operation

### Testing and Commissioning Plan

#### Component Testing:
- Camera pan/tilt/zoom functionality
- Audio capture and playback quality
- Display signal routing and image quality
- Touch panel responsiveness and accuracy

#### Integration Testing:
- Join Microsoft Teams meetings
- Test content sharing from various sources
- Verify camera presets and switching
- Test audio mute/unmute functionality
- Validate room controls (displays, audio, lighting)

#### User Acceptance Testing:
- System demonstration to key stakeholders
- Verification of all required functionality
- Documentation of any requested adjustments
- Final system optimization based on feedback

### Training Materials

#### Quick Reference Guide Outline:
1. Starting the system
2. Joining a scheduled Teams meeting
3. Starting an ad-hoc Teams meeting
4. Sharing content wirelessly and via HDMI
5. Managing camera views
6. Adjusting audio settings
7. Ending meetings and system shutdown

#### Administrator Guide Outline:
1. System overview and equipment inventory
2. Network configuration and requirements
3. Troubleshooting procedures
4. Maintenance guidelines
5. Firmware update procedures
6. Support contact information

### Documentation Deliverables

#### As-Built Documentation:
- Detailed system schematics
- Cable schedules with labels
- Equipment rack layouts
- Room equipment layouts
- Network configuration details

#### Programming Documentation:
- Control system code (commented)
- Touch panel design files
- Configuration settings for all devices
- Network settings and IP addressing scheme

#### Equipment Documentation:
- Equipment inventory with make, model, and serial numbers
- Manufacturer documentation for all components
- Warranty information
- Support contact information

### Maintenance Recommendations

#### Routine Maintenance Tasks:
1. **Monthly (User Performed):**
   - Dust and clean visible equipment
   - Verify camera positioning
   - Check for any loose connections

2. **Quarterly (Technician Performed):**
   - Clean camera lenses
   - Test all system functions
   - Check for firmware updates
   - Verify network connectivity
   - Test backup systems (if applicable)

3. **Biannual (Contractor Performed):**
   - Comprehensive system testing
   - Firmware and software updates
   - Cable inspection and testing
   - Audio system calibration check
   - Control system programming updates as needed

#### Preventive Maintenance Checklist:
- Inspect camera mounts for stability
- Clean air filters in equipment
- Measure and record signal levels
- Test battery backup systems (if applicable)
- Verify control system responsiveness
- Test all source inputs and outputs
- Measure display color accuracy
- Check audio system for noise or distortion
