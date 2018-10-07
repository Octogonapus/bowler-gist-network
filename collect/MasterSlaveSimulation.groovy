@GrabResolver(name='sonatype', root='https://oss.sonatype.org/content/repositories/releases/')
@Grab(group='com.neuronrobotics', module='SimplePacketComsJava', version='0.1.9')

import edu.wpi.SimplePacketComs.device.hephaestus.HephaestusArm;
import Jama.Matrix;

public class HIDSimpleComsDevice extends NonBowlerDevice{
	public HephaestusArm arm;
	public HephaestusArm slave;
	public HIDSimpleComsDevice(int vidIn, int pidIn,int vidSlave, int pidSlave){
		arm = new HephaestusArm(vidIn,pidIn); 
		slave = new HephaestusArm(vidSlave,pidSlave); 
		setScriptingName("hidbowler")
		arm.addEvent(37,{
			def vals =arm.getRawValues()
			for(int i=0;i<vals.size();i++){
				if(vals[i]<-200){
					vals[i]=vals[i]+4096.0
				}
			}
			slave.setRawValues(vals)
		})
	}
	@Override
	public  void disconnectDeviceImp(){
		arm.disconnect()
		slave.disconnect()
		}
	@Override
	public  boolean connectDeviceImp(){
		arm.connect()
		slave.connect()
		}
	@Override
	public  ArrayList<String>  getNamespacesImp(){return null}
}
public class HIDRotoryLink extends AbstractRotoryLink{
	HIDSimpleComsDevice device;
	int index =0;
	int lastPushedVal = 0;
	double velocityTerm = 0;
	double gravityCompTerm = 0;
	/**
	 * Instantiates a new HID rotory link.
	 *
	 * @param c the c
	 * @param conf the conf
	 */
	public HIDRotoryLink(HIDSimpleComsDevice c,LinkConfiguration conf) {
		super(conf);
		index = conf.getHardwareIndex()
		device=c
		if(device ==null)
			throw new RuntimeException("Device can not be null")
		c.arm.addEvent(37,{
			int val= getCurrentPosition();
			if(lastPushedVal!=val){
				//println "Fire Link Listner "+index+" value "+getCurrentPosition()
				try{
					fireLinkListener(val);
				}catch(Exception ex){}
			}
			lastPushedVal=val
		})
		
	}

	/* (non-Javadoc)
	 * @see com.neuronrobotics.sdk.addons.kinematics.AbstractLink#cacheTargetValueDevice()
	 */
	@Override
	public void cacheTargetValueDevice() {
		device.arm.setValues(index,(float)getTargetValue(),(float)velocityTerm ,(float)gravityCompTerm)
	}

	/* (non-Javadoc)
	 * @see com.neuronrobotics.sdk.addons.kinematics.AbstractLink#flush(double)
	 */
	@Override
	public void flushDevice(double time) {
		// auto flushing
	}
	
	/* (non-Javadoc)
	 * @see com.neuronrobotics.sdk.addons.kinematics.AbstractLink#flushAll(double)
	 */
	@Override
	public void flushAllDevice(double time) {
		// auto flushing
	}

	/* (non-Javadoc)
	 * @see com.neuronrobotics.sdk.addons.kinematics.AbstractLink#getCurrentPosition()
	 */
	@Override
	public double getCurrentPosition() {
		return device.arm.getPosition(index);
	}

}

def dev = DeviceManager.getSpecificDevice( "hidbowler",{
	//If the device does not exist, prompt for the connection
	
	HIDSimpleComsDevice d = new HIDSimpleComsDevice(0x3742,0x7,0x3742,0x8)
	d.connect(); // Connect to it.
	LinkFactory.addLinkProvider("hidsimple",{LinkConfiguration conf->
				println "Loading link "
				return new HIDRotoryLink(d,conf)
		}
	)
	println "Connecting new device: "+d
	return d
})
def base =DeviceManager.getSpecificDevice( "HephaestusArm",{
	//If the device does not exist, prompt for the connection
	
	MobileBase m = BowlerStudio.loadMobileBaseFromGit(
		"https://github.com/madhephaestus/SeriesElasticActuator.git",
		"HIDarm.xml"
		)
	if(m==null)
		throw new RuntimeException("Arm failed to assemble itself")
	println "Connecting new device robot arm "+m
	return m
})

return null
