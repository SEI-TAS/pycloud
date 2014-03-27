package edu.cmu.sei.cloudlet.client.ui;

import edu.cmu.sei.cloudlet.client.CurrentCloudlet;
import edu.cmu.sei.cloudlet.client.R;
import edu.cmu.sei.cloudlet.client.caching.ui.ListServicesActivity;
import edu.cmu.sei.cloudlet.client.ondemand.ui.ModulesList;
import edu.cmu.sei.cloudlet.client.push.ui.CloudletAppsListActivity;
import edu.cmu.sei.cloudlet.client.synth.ui.OverlayList;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;

/**
 * Simple activity to choose between different cloudlet techniques.
 * @author secheverria
 *
 */
public class ProcessSelectionActivity extends Activity
{
    @Override
    protected void onCreate(Bundle savedInstanceState) 
    {
        // Base and layout setup.
        super.onCreate(savedInstanceState);
        setContentView(R.layout.process_selection);
        
        // Load cloudlet information.
        ConnectionInfoFragment connInfoFragment = (ConnectionInfoFragment) getFragmentManager().findFragmentById(R.id.connInfoPanel);
        connInfoFragment.setCloudletInfo(CurrentCloudlet.name, CurrentCloudlet.ipAddress);            
        
        // Setup button to go to VM Synthesis activity.
        Button vmSynthButton = (Button) findViewById(R.id.vmsynthproc);       
        vmSynthButton.setOnClickListener(new OnClickListener() 
        {
            @Override
            public void onClick(View v) 
            {
                Intent intent = new Intent(ProcessSelectionActivity.this, OverlayList.class);
                startActivity(intent);
            }
        });
        
        // Setup button to go to Cloudlet Push activity.
        Button pushButton = (Button) findViewById(R.id.cloudletpushproc);       
        pushButton.setOnClickListener(new OnClickListener() 
        {
            @Override
            public void onClick(View v) 
            {
                Intent intent = new Intent(ProcessSelectionActivity.this, CloudletAppsListActivity.class);
                startActivity(intent);
            }
        });
        
        
        // Setup button to go to On-Demand Provisioning activity.
        Button odpButton = (Button) findViewById(R.id.odpproc);       
        odpButton.setOnClickListener(new OnClickListener() 
        {
            @Override
            public void onClick(View v) 
            {
                Intent intent = new Intent(ProcessSelectionActivity.this, ModulesList.class);
                startActivity(intent);
            }
        });

        // Setup button to go to Cloudlet Push activity.
        Button cachingButton = (Button) findViewById(R.id.caching_btn);
        cachingButton.setOnClickListener(new OnClickListener()
        {
            @Override
            public void onClick(View v)
            {
                Intent intent = new Intent(ProcessSelectionActivity.this, ListServicesActivity.class);
                startActivity(intent);
            }
        });
    }
}
