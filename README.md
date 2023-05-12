# taipy-integration-testing
This repository holds GH actions that have the purpose of testing Taipy Enterprise and all its dependencies.

The performance tests are executed via an API call on the GitHub Action called `benchmark` which is triggered by Taipy-Core during merges.

To ensure that the tests are relevant and consistent, we always use the same machine configuration. This machine is a VM on Azure which has a GitHub Runner configured on it. The machine is started and stopped on demand when the `benchmark` GitHub Action is executed. You can refer to the "GitHub Runner" documentation below to access this machine.

The result of each execution is stored on an Azure Blob Storage for future reference and analysis.


# GitHub Runner

The GitHub Action `benchmark` is running on a dedicated GitHub Runner for reliability in the result. 
You can find this runner here https://portal.azure.com/#@avaiga.com/resource/subscriptions/375d1919-3cdc-41d1-978f-9c4efaa3a46e/resourceGroups/github-runner/providers/Microsoft.Compute/virtualMachines/integration-testing-runner/overview.
The Runner is keeping results in an Azure Blob Storage in the same subscription.

Azure Information:
- Subscription: integration-testing
- Resource Group: github-runner

## Accessing to the Runner for maintenance

The Virtual Machine on which the GitHub Runner is running does not have a public IP address for security reason.
To be able to access to it, you have to use an Azure Bastion.

### Creating an Azure Bastion:

- Navigate to the VM in the Azure portal.
- Click on the "Connect" button at the top of the VM's overview page.
- In the "Connect" pane, select "Bastion" as the type of connection.
- Configure the Bastion settings as required, such as the virtual network and subnet, and click "Create".


### Connecting to the VM with Azure Bastion

- Navigate to the VM in the Azure portal.
- Click on the "Connect" button at the top of the VM's overview page.
- In the "Connect" pane, select "Bastion" as the type of connection.
- Click "Use Bastion".
- In the Azure Bastion pane, enter the following information:
    Username: taipy
    Authentication Type: Password from Azure Key Vault
    Key Vault: github-runner-key
    Secret: taipy
- Click "Connect".

### Delete the Azure Bastion

It is important to note that Azure Bastion is charged hourly, so it is recommended that you delete it once you have completed your operations. To delete the Azure Bastion, follow these steps:
- Navigate to the Bastion resource in the Azure portal.
- Click "Delete".
- Confirm the deletion when prompted.
