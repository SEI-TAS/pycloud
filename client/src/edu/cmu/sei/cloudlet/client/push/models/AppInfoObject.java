package edu.cmu.sei.cloudlet.client.push.models;

public class AppInfoObject {
	
	private String name;
	private String description;
	private String appPackage;
	private String serviceId;
	private String tags;
	private String minRequiredVersion;
	private String sha1hash;
	private String version;
	
	
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
    public String getPackage() {
        return appPackage;
    }
    public void setPackage(String appPackage) {
        this.appPackage = appPackage;
    }
    public String getServiceId() {
        return serviceId;
    }
    public void setServiceId(String serviceId) {
        this.serviceId = serviceId;
    }       
	public String getTags() {
		return tags;
	}
	public void setTags(String tags) {
		this.tags = tags;
	}
	public String getMinRequiredVersion() {
		return minRequiredVersion;
	}
	public void setMinRequiredVersion(String minRequiredVersion) {
		this.minRequiredVersion = minRequiredVersion;
	}
	public String getSha1hash() {
		return sha1hash;
	}
	public void setSha1hash(String sha1hash) {
		this.sha1hash = sha1hash;
	}
	public String getVersion() {
		return version;
	}
	public void setVersion(String version) {
		this.version = version;
	}

}
