# CatGenie Integration

![GitHub release (latest by date)](https://img.shields.io/github/v/release/kclif9/hasscatgenie)
![GitHub](https://img.shields.io/github/license/kclif9/hasscatgenie)

This is a custom integration for Home Assistant to integrate CatGenie AI self-cleaning litter boxes.

This integration is currently the test version of the integration being submitted to Home Assistant for adding to the core integrations. When HA core is at feature parity, this HACS integration will be retired.

## Installation

### Prerequisites

- Home Assistant (version 2023.3.0 or later recommended)
- A CatGenie AI self-cleaning litter box
- A valid CatGenie account (phone number registered in the CatGenie app)
- Your CatGenie device must be connected to the internet

### HACS (Home Assistant Community Store)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kclif9&repository=hasscatgenie)

1. Ensure that [HACS](https://hacs.xyz/) is installed.
2. Go to HACS > Integrations.
3. Click on the three dots in the top right corner and select "Custom repositories".
4. Add the repository URL: `https://github.com/kclif9/hasscatgenie` and select "Integration".
5. Find "CatGenie" in the list and click "Install".
6. Restart Home Assistant after installation.

### Manual Installation

1. Download the `custom_components` directory from the [latest release](https://github.com/kclif9/hasscatgenie/releases/latest).
2. Copy the `custom_components/catgenie` directory to your Home Assistant configuration directory (typically `/config/custom_components/`).
3. Restart Home Assistant after installation.

## Configuration

### Setup Process

The integration uses **SMS verification** for authentication:

1. In the Home Assistant UI, navigate to `Configuration` > `Devices & Services`.
2. Click the `+ Add Integration` button.
3. Search for `CatGenie` and select it.
4. Enter your country code and phone number (the one registered with your CatGenie account).
5. Enter the 6-digit SMS verification code sent to your phone.
6. Once verified, the integration will automatically discover all your CatGenie devices.

### Configuration Notes

- Each CatGenie device under your account will be added as a separate device.
- Reauthentication is supported if your session expires — Home Assistant will prompt you to re-verify via SMS.

## Features

- **Sensors**: Cleaning status, SaniSolution level, clean progress, cycle count, and last clean time

## Supported Devices

- **CatGenie AI**: Self-cleaning litter boxes manufactured by PetNovations

## Entities

### Sensors

| Sensor | Device Class | Unit | Enabled by Default |
|---|---|---|---|
| SaniSolution level | — | — | Yes |
| Status | Enum (idle/cleaning) | — | Yes |
| Clean progress | — | % | Yes |
| Total cycles | — | — | No |
| Last clean | Timestamp | — | No |

## Data Updates

The integration updates data using the following approach:

- **Update Frequency**: Data is polled from the CatGenie cloud service every 60 seconds.
- **Update Method**: The integration uses a cloud polling approach as specified by the `iot_class: cloud_polling` in the integration manifest.
- **Coordinator Pattern**: Each device has its own update coordinator to fetch the latest state.
- **Token Refresh**: Authentication tokens are automatically refreshed when they expire.

## Example Use Cases

### Notify When Cleaning Completes

```yaml
automation:
  - alias: "CatGenie cleaning complete"
    trigger:
      platform: state
      entity_id: sensor.catgenie_status
      from: "cleaning"
      to: "idle"
    action:
      service: notify.mobile_app
      data:
        message: "CatGenie has finished cleaning!"
```

### Alert When SaniSolution Is Low

```yaml
automation:
  - alias: "CatGenie SaniSolution low"
    trigger:
      platform: numeric_state
      entity_id: sensor.catgenie_sani_solution
      below: 10
    action:
      service: notify.mobile_app
      data:
        message: "CatGenie SaniSolution is running low. Time to refill!"
```

## Known Limitations

- **Cloud Dependency**: The integration relies on the CatGenie cloud service, so internet connectivity is required for operation.
- **Read-Only**: The integration currently only exposes sensors. Starting a cleaning cycle from Home Assistant is not yet supported.

## Troubleshooting

If you encounter issues, please check the Home Assistant logs for any error messages related to the `catgenie` integration.

### Common Issues

#### Authentication Errors

- **Symptom**: Unable to authenticate, entities show as unavailable
- **Possible Causes**:
  - Expired session token
  - Phone number not registered with CatGenie
- **Solutions**:
  - Go to the integration in Home Assistant, click "Configure" and re-authenticate via SMS
  - Verify your phone number is correct and registered in the CatGenie app

#### Connection Errors

- **Symptom**: Entities unavailable
- **Possible Causes**:
  - CatGenie cloud service is down
  - Your internet connection is disrupted
  - Your CatGenie device is offline
- **Solutions**:
  - Check your internet connection
  - Verify the CatGenie device is powered on and connected to WiFi
  - Check if the official CatGenie app can see your device

### Log Checking

To check your logs for troubleshooting:

1. Go to Home Assistant "Settings" > "System" > "Logs"
2. Filter for "catgenie" to see messages specific to this integration
3. Look for error messages that can help identify the issue

If you need further assistance, please open an issue on the [GitHub repository](https://github.com/kclif9/hasscatgenie/issues) with the following information:

- Description of the problem
- Relevant log entries
- Home Assistant version
- Integration version

## Removing the Integration

1. Go to `Configuration` > `Devices & Services`.
2. Find the CatGenie integration card and click on it.
3. Click the three dots in the top-right corner and select "Delete".
4. Confirm the deletion.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Home Assistant](https://www.home-assistant.io/)
- [HACS](https://hacs.xyz/)
- [CatGenie API Library](https://github.com/kclif9/catgenie-api)
- [PrimeAutomation](https://github.com/PrimeAutomation/petnovations) who did the original CatGenie implementation.
