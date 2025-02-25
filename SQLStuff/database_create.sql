USE [master]
GO
/****** Object:  Database [CoralClientSeller]    Script Date: 11/30/2024 5:39:16 PM ******/
CREATE DATABASE [CoralClientSeller]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'CoralClientSeller', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\CoralClientSeller.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'CoralClientSeller_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\CoralClientSeller_log.ldf' , SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT, LEDGER = OFF
GO
ALTER DATABASE [CoralClientSeller] SET COMPATIBILITY_LEVEL = 160
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [CoralClientSeller].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [CoralClientSeller] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [CoralClientSeller] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [CoralClientSeller] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [CoralClientSeller] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [CoralClientSeller] SET ARITHABORT OFF 
GO
ALTER DATABASE [CoralClientSeller] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [CoralClientSeller] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [CoralClientSeller] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [CoralClientSeller] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [CoralClientSeller] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [CoralClientSeller] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [CoralClientSeller] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [CoralClientSeller] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [CoralClientSeller] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [CoralClientSeller] SET  DISABLE_BROKER 
GO
ALTER DATABASE [CoralClientSeller] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [CoralClientSeller] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [CoralClientSeller] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [CoralClientSeller] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [CoralClientSeller] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [CoralClientSeller] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [CoralClientSeller] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [CoralClientSeller] SET RECOVERY FULL 
GO
ALTER DATABASE [CoralClientSeller] SET  MULTI_USER 
GO
ALTER DATABASE [CoralClientSeller] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [CoralClientSeller] SET DB_CHAINING OFF 
GO
ALTER DATABASE [CoralClientSeller] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [CoralClientSeller] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [CoralClientSeller] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [CoralClientSeller] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
EXEC sys.sp_db_vardecimal_storage_format N'CoralClientSeller', N'ON'
GO
ALTER DATABASE [CoralClientSeller] SET QUERY_STORE = ON
GO
ALTER DATABASE [CoralClientSeller] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 1000, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO
USE [CoralClientSeller]
GO
/****** Object:  User [CoralClientSellerApp]    Script Date: 11/30/2024 5:39:16 PM ******/
CREATE USER [CoralClientSellerApp] FOR LOGIN [CoralClientSellerApp] WITH DEFAULT_SCHEMA=[dbo]
GO
ALTER ROLE [db_owner] ADD MEMBER [CoralClientSellerApp]
GO
ALTER ROLE [db_datareader] ADD MEMBER [CoralClientSellerApp]
GO
ALTER ROLE [db_datawriter] ADD MEMBER [CoralClientSellerApp]
GO
/****** Object:  Table [dbo].[roles]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[roles](
	[role_id] [int] IDENTITY(1,1) NOT NULL,
	[name] [nvarchar](50) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[role_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[permissions]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[permissions](
	[permission_id] [int] IDENTITY(1,1) NOT NULL,
	[name] [nvarchar](50) NOT NULL,
	[description] [varchar](100) NULL,
PRIMARY KEY CLUSTERED 
(
	[permission_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[role_permissions]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[role_permissions](
	[role_id] [int] NOT NULL,
	[permission_id] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[role_id] ASC,
	[permission_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[vw_permissions]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
create view [dbo].[vw_permissions] as
select r.role_id,r.name as role_name,
p.*
from roles r 
join role_permissions rp on r.role_id = rp.role_id
join permissions p on rp.permission_id = p.permission_id
GO
/****** Object:  Table [dbo].[Bill]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Bill](
	[BillID] [int] IDENTITY(1,1) NOT NULL,
	[VisitID] [int] NOT NULL,
	[TotalAmount] [decimal](10, 2) NOT NULL,
	[IsPaid] [bit] NOT NULL,
	[CreatedAt] [datetime] NULL,
	[PaidAt] [datetime] NULL,
	[Notes] [nvarchar](max) NULL,
PRIMARY KEY CLUSTERED 
(
	[BillID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BillLineItem]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BillLineItem](
	[LineItemID] [int] IDENTITY(1,1) NOT NULL,
	[BillID] [int] NOT NULL,
	[Description] [nvarchar](255) NOT NULL,
	[Quantity] [int] NOT NULL,
	[UnitPrice] [decimal](10, 2) NOT NULL,
	[TotalPrice]  AS ([Quantity]*[UnitPrice]) PERSISTED,
PRIMARY KEY CLUSTERED 
(
	[LineItemID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[consignment_products]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[consignment_products](
	[product_id] [int] IDENTITY(1,1) NOT NULL,
	[name] [nvarchar](100) NOT NULL,
	[description] [nvarchar](max) NULL,
	[price] [decimal](10, 2) NOT NULL,
	[image_url] [nvarchar](255) NULL,
	[item_type_id] [int] NULL,
	[item_subtype_id] [int] NULL,
	[seller_id] [int] NULL,
	[featured] [bit] NULL,
	[order_status] [varchar](5) NULL,
PRIMARY KEY CLUSTERED 
(
	[product_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[item_subtypes]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[item_subtypes](
	[item_subtype_id] [int] IDENTITY(1,1) NOT NULL,
	[item_type_id] [int] NULL,
	[name] [nvarchar](50) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[item_subtype_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[item_types]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[item_types](
	[item_type_id] [int] IDENTITY(1,1) NOT NULL,
	[name] [nvarchar](50) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[item_type_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[maintenance_visits]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[maintenance_visits](
	[visit_id] [int] IDENTITY(1,1) NOT NULL,
	[customer_id] [int] NOT NULL,
	[before_picture] [varchar](255) NULL,
	[ammonia] [float] NULL,
	[nitrite] [float] NULL,
	[nitrate] [float] NULL,
	[ph] [float] NULL,
	[phosphates] [float] NULL,
	[calcium] [float] NULL,
	[magnesium] [float] NULL,
	[alkalinity] [float] NULL,
	[notes] [text] NULL,
	[recommendations] [text] NULL,
	[after_picture] [varchar](255) NULL,
	[date_of_visit] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[visit_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[orders]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[orders](
	[order_id] [int] IDENTITY(1,1) NOT NULL,
	[product_id] [int] NULL,
	[buyer_id] [int] NULL,
	[seller_id] [int] NULL,
	[order_date] [datetime] NULL,
	[product_dropoff] [date] NULL,
	[product_pickup] [date] NULL,
	[payment_status] [varchar](50) NULL,
	[order_status] [varchar](5) NULL,
PRIMARY KEY CLUSTERED 
(
	[order_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[users]    Script Date: 11/30/2024 5:39:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[users](
	[user_id] [int] IDENTITY(1,1) NOT NULL,
	[username] [nvarchar](50) NOT NULL,
	[password_hash] [nvarchar](128) NOT NULL,
	[email] [nvarchar](100) NOT NULL,
	[role_id] [int] NULL,
	[first_name] [varchar](150) NULL,
	[last_name] [varchar](150) NULL,
	[DOB] [date] NULL,
	[phone_number] [varchar](20) NULL,
	[is_maintenance] [bit] NULL,
	[in_store_credit] [float] NULL,
	[PasswordReset] [bit] NULL,
PRIMARY KEY CLUSTERED 
(
	[user_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[email] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[username] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Bill] ADD  DEFAULT ((0)) FOR [IsPaid]
GO
ALTER TABLE [dbo].[Bill] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO
ALTER TABLE [dbo].[BillLineItem] ADD  DEFAULT ((1)) FOR [Quantity]
GO
ALTER TABLE [dbo].[maintenance_visits] ADD  DEFAULT (getdate()) FOR [date_of_visit]
GO
ALTER TABLE [dbo].[orders] ADD  DEFAULT (getdate()) FOR [order_date]
GO
ALTER TABLE [dbo].[Bill]  WITH CHECK ADD FOREIGN KEY([VisitID])
REFERENCES [dbo].[maintenance_visits] ([visit_id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[BillLineItem]  WITH CHECK ADD  CONSTRAINT [FK_BillLineItem_Bill] FOREIGN KEY([BillID])
REFERENCES [dbo].[Bill] ([BillID])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[BillLineItem] CHECK CONSTRAINT [FK_BillLineItem_Bill]
GO
ALTER TABLE [dbo].[consignment_products]  WITH CHECK ADD FOREIGN KEY([item_type_id])
REFERENCES [dbo].[item_types] ([item_type_id])
GO
ALTER TABLE [dbo].[consignment_products]  WITH CHECK ADD FOREIGN KEY([item_subtype_id])
REFERENCES [dbo].[item_subtypes] ([item_subtype_id])
GO
ALTER TABLE [dbo].[consignment_products]  WITH CHECK ADD FOREIGN KEY([seller_id])
REFERENCES [dbo].[users] ([user_id])
GO
ALTER TABLE [dbo].[item_subtypes]  WITH CHECK ADD FOREIGN KEY([item_type_id])
REFERENCES [dbo].[item_types] ([item_type_id])
GO
ALTER TABLE [dbo].[maintenance_visits]  WITH CHECK ADD FOREIGN KEY([customer_id])
REFERENCES [dbo].[users] ([user_id])
GO
ALTER TABLE [dbo].[orders]  WITH CHECK ADD FOREIGN KEY([buyer_id])
REFERENCES [dbo].[users] ([user_id])
GO
ALTER TABLE [dbo].[orders]  WITH CHECK ADD FOREIGN KEY([product_id])
REFERENCES [dbo].[consignment_products] ([product_id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[orders]  WITH CHECK ADD FOREIGN KEY([seller_id])
REFERENCES [dbo].[users] ([user_id])
GO
ALTER TABLE [dbo].[role_permissions]  WITH CHECK ADD FOREIGN KEY([permission_id])
REFERENCES [dbo].[permissions] ([permission_id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[role_permissions]  WITH CHECK ADD FOREIGN KEY([role_id])
REFERENCES [dbo].[roles] ([role_id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[users]  WITH CHECK ADD FOREIGN KEY([role_id])
REFERENCES [dbo].[roles] ([role_id])
GO
USE [master]
GO
ALTER DATABASE [CoralClientSeller] SET  READ_WRITE 
GO
