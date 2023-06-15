
using Examples.BadDesign.CarExample;
using Examples.BadDesign.CarExample.WarehouseEntities;
using Examples.BadDesign.CarExample.CarParts;

namespace Examples.BadDesign.CarExample {

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
    Examples.BadDesign.CarExample.WarehouseEntities.Car getWarehouseCarWhere(String query) {
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
    User getUserFromWarehouseCar(Examples.BadDesign.CarExample.WarehouseEntities.Car item) {
        return null;
    }
    Customer getCustomerFromComplaint(Complaints complaint) {
        return null;
    }
    Car getWarehouseCarFromUser(Examples.BadDesign.CarExample.WarehouseEntities.Car user) {
        return null;
    }
    Invoice getInvoiceFromCustomer(Customer c) {
        return null;
    }
    Complaints getComplaintsFromWarehouseCar(Examples.BadDesign.CarExample.WarehouseEntities.Car item) {
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
}