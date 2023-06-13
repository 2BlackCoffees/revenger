package Examples.BetterDesign.CarExample;

import Examples.BetterDesign.DBCar;
import Examples.BetterDesign.CarExample.CarParts.Doors;
import Examples.BetterDesign.CarExample.CarParts.Driver;
import Examples.BetterDesign.CarExample.CarParts.Seats;
import Examples.BetterDesign.CarExample.CarParts.Wheels;

class Vehicle
{
    int speed;
    DBCar db;
    public Vehicle()
    {

    }
    void setSpeed(int speed) {
        this.speed = speed;
    }
    int getSpeed() {
        return speed;
    }
}
public class Car extends Vehicle {
    Wheels wheels;
    Seats seats;
    Driver driver;
    Doors doors;

    public Car()
    {}
    void createCar(Doors doors)
    {
    }
}
