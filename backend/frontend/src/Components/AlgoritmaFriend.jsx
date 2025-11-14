import UserIcon from "./Element/icon/UserIcon";

const AlgoritmaFriend = () => {
    const list = [
        {
  nama: "Dika",
  tag: "dikzzy"
},
{
  nama: "Rara",
  tag: "rarahh"
},
{
  nama: "Bagas",
  tag: "gasbro"
},
{
  nama: "Nisa",
  tag: "nis.aa"
},
{
  nama: "Eka",
  tag: "ekzzy"
},
{
  nama: "Rio",
  tag: "riowkwk"
},
{
  nama: "Tio",
  tag: "tiowae"
},
{
  nama: "Mey",
  tag: "mey2cute"
},
{
  nama: "Rendy",
  tag: "rendyxz"
},
{
  nama: "Lala",
  tag: "lalzzz"
},
{
  nama: "Fajar",
  tag: "fjr.ganteng"
},
{
  nama: "Cika",
  tag: "ckaa_"
}


    ]
  return (
  <div className="overflow-x-auto px-3 sm:px-5">
  <div className="flex gap-5 sm:gap-7 mt-4 mb-16 w-max">
    {list.map((user) => (
      <div
        key={user.id}
        className="relative border p-5 sm:p-6 rounded-xl flex flex-col justify-center items-center min-w-[180px] sm:min-w-[220px] font-mono"
      >
        <button className="absolute top-1.5 right-1.5 text-gray-400 hover:rotate-45 duration-300 text-sm sm:text-base">
          ✕
        </button>

        <UserIcon
          className="w-5 h-5 sm:w-6 sm:h-6 text-gray-400"
          classFrist={"w-14 h-14 sm:w-16 sm:h-16"}
          classSecond={"w-14 h-14 sm:w-16 sm:h-16"}
        />
        <h1 className="text-lg sm:text-xl mt-2">{user.nama}</h1>
        <p className="text-gray-400 text-sm">@{user.tag}</p>
        <button className="cursor-pointer mt-4 bg-white text-black px-4 py-1.5 rounded-lg hover:bg-black hover:text-white border border-gray-600 duration-200 text-sm">
          Follow
        </button>
      </div>
    ))}
  </div>
</div>

  );
};


export default AlgoritmaFriend