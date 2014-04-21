package edu.cmu.sei.cloudlet.client.ui;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import edu.cmu.sei.cloudlet.client.R;

/**
 * User: jdroot
 * Date: 4/15/14
 * Time: 10:43 AM
 */
public class NewProcessSelectionActivity extends Activity
{
    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.new_process_selection);

        final Button cloudletButton = (Button) findViewById(R.id.cloudlet_selection);
        final Button serviceButton = (Button) findViewById(R.id.service_selection);

        //Make the old cloudlet app run
        cloudletButton.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                Intent i = new Intent(NewProcessSelectionActivity.this, CloudletDiscoveryActivity.class);
                startActivity(i);
            }
        });

        //Start the service selection activity
        serviceButton.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                Intent i = new Intent(NewProcessSelectionActivity.this, CloudletSelectionActivity.class);
                startActivity(i);
            }
        });
    }
}
