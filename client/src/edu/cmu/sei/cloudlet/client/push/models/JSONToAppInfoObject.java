package edu.cmu.sei.cloudlet.client.push.models;

import java.util.ArrayList;
import java.util.List;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class JSONToAppInfoObject {
	
	public static final String NAME = "name";
	public static final String DESCRIPTION = "description";
	public static final String PACKAGE = "package";
	public static final String SERVICE_ID = "serviceId";
	public static final String TAGS = "tags";
	public static final String MIN_REQUIRED_VERSION = "minrequired_version";
	public static final String SHA1HASH = "sha1hash";
	public static final String VERSION = "version";
	public static final String APPS = "apps";
	
	public static List<AppInfoObject> getAppInfoObjectsFromJSONString(String jsonString) throws JSONException{
		
		List<AppInfoObject> list = new ArrayList<AppInfoObject>();
			JSONObject jsonObject = new JSONObject(jsonString);
			JSONArray jsonArray = jsonObject.getJSONArray(APPS);
			JSONObject jsonAppInfo;
			for(int i=0; i < jsonArray.length(); i++){
				jsonAppInfo = jsonArray.getJSONObject(i);
				list.add(toAppInfoObject(jsonAppInfo));
			}
		return list;
	}
	
	public static AppInfoObject toAppInfoObject(JSONObject jsonObject){
		
		if( jsonObject == null )
			return null;
		
		 AppInfoObject appInfoObject = new AppInfoObject();
		try {
			appInfoObject.setName(jsonObject.getString(NAME));
		} catch (JSONException e) {e.printStackTrace();}
		try {
			appInfoObject.setDescription(jsonObject.getString(DESCRIPTION));
		} catch (JSONException e) {e.printStackTrace();}
        try {
            appInfoObject.setPackage(jsonObject.getString(PACKAGE));
        } catch (JSONException e) {e.printStackTrace();}
        try {
            appInfoObject.setServiceId(jsonObject.getString(SERVICE_ID));
        } catch (JSONException e) {e.printStackTrace();}
        
		try {
			appInfoObject.setTags(jsonObject.getString(TAGS));
		} catch (JSONException e) {e.printStackTrace();}
		try {
			appInfoObject.setMinRequiredVersion(jsonObject.getString(MIN_REQUIRED_VERSION));
		} catch (JSONException e) {e.printStackTrace();}
		try {
			appInfoObject.setSha1hash(jsonObject.getString(SHA1HASH));
		} catch (JSONException e) {e.printStackTrace();}
		try {
			appInfoObject.setVersion(jsonObject.getString(VERSION));
		} catch (JSONException e) {e.printStackTrace();}
		return appInfoObject;
	}
	
	public static AppInfoObject toAppInfoObject(String jsonString){
		
		if( jsonString == null )
			return null;
		
		JSONObject jsonObj = null;
		try {
			jsonObj = new JSONObject(jsonString);
		} catch (JSONException e) {
			e.printStackTrace();
		}
		return toAppInfoObject(jsonObj);
	}
}
