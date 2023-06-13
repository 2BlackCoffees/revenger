package Examples.BetterDesign;

import Examples.BetterDesign.CarExample.Car;
import Examples.BetterDesign.CarExample.CarParts.Doors;
import Examples.BetterDesign.CarExample.CarParts.Driver;
import Examples.BetterDesign.CarExample.CarParts.Seats;
import Examples.BetterDesign.CarExample.CarParts.Wheels;


public class DBCar {
    DBCar() {

    }

    String[] getCarsForDriver(Driver driver) {
        return null;
    }

    void updateCar(Car car, Seats seats) {
    }

    void updateCar(Car car, Doors doors) {
    }

    void sellCarTo(Car car, Driver driver) {
    }
    Car getCarFromDriver(Driver d)
    {
        return new Car();
    }
    Driver getDriverFromCar(Car c)
    {
        return new Driver();
    }
    Wheels getWheelsFromCar(Car c)
    {
        return null;
    }
    Doors getDoorsFromCar(Car c)
    {
        return null;
    }
    Seats getSeatsFromCar(Car c)
    {
        return null;
    }
} 