import SideMenu from "../SideMenu/SideMenu";
import TreeTable from "../Table/TreeTable";
import TopBar from "../TopBar/TopBar";

const Dashboard = () : JSX.Element => {
  return (
    <div className="w-full h-full">
      <div className="flex flex-row w-full justify-between">
        <SideMenu />
        <TopBar />
        <div className="w-full px-16 pt-64 bg-lightGray">
          <TreeTable />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
