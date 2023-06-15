package Examples.BadDesign;

import Examples.BadDesign.CarExample.Car;
import Examples.BadDesign.CarExample.CarParts.Doors;
import Examples.BadDesign.CarExample.CarParts.Driver;
import Examples.BadDesign.CarExample.CarParts.Seats;
import Examples.BadDesign.CarExample.CarParts.Wheels;
import Examples.BadDesign.WarehouseEntitities.Complaints;
import Examples.BadDesign.WarehouseEntitities.Customer;
import Examples.BadDesign.WarehouseEntitities.Invoice;
import Examples.BadDesign.WarehouseEntitities.User;

public class DB {
    DB() {

    }

    String[] get(String queryString) {
        return null;
    }
    String[] getCarsWhere(String whereQueryString) {
        return null;
    }
    void set(String queryString) {
    }
    void update(String queryString) {
    }

    User getUserWhere(String query) {
        return null;
    }
    Customer getCustomerWhere(String query) {
        return null;
    }
    Examples.BadDesign.WarehouseEntitities.Car getWarehouseCarWhere(String query) {
        return null;
    }
    Invoice getInvoiceWhere(String query) {
        return null;
    }
    Complaints getComplaintsWhere(String query) {
        return null;
    }
    Customer getFirstCustomerWhere(String query) {
        return null;
    }
    User getUserFromWarehouseCar(Examples.BadDesign.WarehouseEntitities.Car item) {
        return null;
    }
    Customer getCustomerFromComplaint(Complaints complaint) {
        return null;
    }
    Car getWarehouseCarFromUser(Examples.BadDesign.WarehouseEntitities.Car user) {
        return null;
    }
    Invoice getInvoiceFromCustomer(Customer c) {
        return null;
    }
    Complaints getComplaintsFromWarehouseCar(Examples.BadDesign.WarehouseEntitities.Car item) {
        return null;
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