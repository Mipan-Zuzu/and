const Items = () => {
    const nav = [
        {
            title : "Postingan"
        },
        {
            title : "Teman"
        },
        {
            title : "Catatan"
        },
        {
            title : "Status"
        },
        {
            title : "Viral"
        },
        {
            title : "Berita"
        }
    ]
  return (
    <div className="px-4 sm:px-8 md:px-10 mt-4 overflow-x-scroll font-mono">
  <div className="flex gap-2 sm:gap-3 flex-nowrap w-max">
    <a className="p-1 sm:p-2 cursor-pointer font-semibold text-xs sm:text-sm md:text-base px-3 sm:px-4 border bg-white text-black rounded-2xl hover:text-white hover:bg-black duration-300">
      Semua
    </a>

    {nav.map((item, index) => (
      <a
        key={index}
        className="p-1 sm:p-2 cursor-pointer font-semibold text-xs sm:text-sm md:text-base px-3 sm:px-4 border rounded-3xl text-white hover:bg-white hover:text-black duration-300"
      >
        {item.title}
      </a>
    ))}
  </div>
</div>

  );
};

export default Items