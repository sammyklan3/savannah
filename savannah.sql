-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 13, 2023 at 12:36 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `savannah`
--

-- --------------------------------------------------------

--
-- Table structure for table `followers`
--

CREATE TABLE `followers` (
  `id` int(11) NOT NULL,
  `follower_id` varchar(32) NOT NULL,
  `following_id` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `followers`
--

INSERT INTO `followers` (`id`, `follower_id`, `following_id`) VALUES
(20, '2d14dbddbca6513c7fe711e2fe61294b', '2d14dbddbca6513c7fe711e2fe61294b'),
(29, 'sammyklane', '97'),
(38, 'washira', '98');

-- --------------------------------------------------------

--
-- Table structure for table `posts`
--

CREATE TABLE `posts` (
  `post_id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `title` varchar(50) NOT NULL,
  `likes` int(11) NOT NULL,
  `upload_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `file_type` varchar(50) NOT NULL,
  `file_size` int(11) NOT NULL,
  `user_id` varchar(32) DEFAULT NULL,
  `caption` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `posts`
--

INSERT INTO `posts` (`post_id`, `filename`, `title`, `likes`, `upload_date`, `file_type`, `file_size`, `user_id`, `caption`) VALUES
(7, 'NukYviiwvu.jpg', 'Nairobi, Kenya', 0, '2023-05-13 08:57:46', 'image/jpeg', 127097, 'ccfbca1d05a03ab3174aea9136a6e921', 'lights up bwoy'),
(8, 'eFBkNkMtSY.jpg', 'In my world lol', 0, '2023-05-13 09:05:07', 'image/jpeg', 460791, 'ccfbca1d05a03ab3174aea9136a6e921', 'i have much money'),
(10, 'TLMZTUHjxE.mp4', 'Funny clips', 0, '2023-05-13 09:23:56', 'video/mp4', 4087934, 'ccfbca1d05a03ab3174aea9136a6e921', '#viral #funnyclip https://www.instagram.com/');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `user_id` varchar(32) NOT NULL,
  `email` varchar(100) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `phone` bigint(11) NOT NULL,
  `profile_pic` varchar(225) NOT NULL DEFAULT 'default.png',
  `bio` varchar(500) NOT NULL,
  `reg_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `user_id`, `email`, `username`, `password`, `phone`, `profile_pic`, `bio`, `reg_date`) VALUES
(97, '2d14dbddbca6513c7fe711e2fe61294b', 'sammyklane@gmail.com', 'washira', '$2b$12$vK6iO3BFvSckdfafORMyjuL3p.t0xzUq67XYN5sVCMk/JSiweAqEK', 734233456, '7c4d0bf4-3961-4625-99db-d88431303252.jpg', 'Avid reader, passionate writer, and relentless dreamer. Crafting words to ignite minds and inspire hearts. 📚✍️🌌', '2023-05-12 13:21:33'),
(98, 'ccfbca1d05a03ab3174aea9136a6e921', 'sammyklane@outlook.com', 'sammyklane', '$2b$12$U097tDuJhMoUAFfwTB17Ou5XKIUBt9d9fiCV5RSiN9DUuRKLawPw.', 795012442, 'ae3758d1-2ac8-4522-8203-10a571c310ac.jpg', '🌟 Dream chaser | 🎉 Adventure seeker | 🌈 Optimistic soul | 🚀 Wanderlust enthusiast | 🔥 Coffee addict | 🎶 Music lover | 📷 Photography enthusiast | 💫 Star gazer | 🦄 Believer in magic | ✨ Spreading positive vibes', '2023-05-13 08:56:39');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `followers`
--
ALTER TABLE `followers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `follower_id` (`follower_id`),
  ADD UNIQUE KEY `following_id` (`following_id`);

--
-- Indexes for table `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`post_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `id` (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `followers`
--
ALTER TABLE `followers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT for table `posts`
--
ALTER TABLE `posts`
  MODIFY `post_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=99;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
